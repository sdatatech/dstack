package aws

import (
	"context"
	"errors"
	"fmt"
	"io"
	"strings"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/feature/s3/manager"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/dstackai/dstack/runner/internal/backend/base"
	"github.com/dstackai/dstack/runner/internal/gerrors"
)

var ErrTagNotFound = errors.New("tag not found")

type AWSStorage struct {
	s3        *s3.Client
	bucket    *string
	namespace string
	uploader  *manager.Uploader
	//downloader *manager.Downloader
}

func NewAWSStorage(bucket, namespace string) (*AWSStorage, error) {
	ctx := context.TODO()
	region, err := getBucketRegion(ctx, bucket)
	if err != nil {
		return nil, gerrors.Wrap(err)
	}
	cfg, err := config.LoadDefaultConfig(ctx, config.WithRegion(region))
	if err != nil {
		return nil, gerrors.Wrap(err)
	}
	client := s3.NewFromConfig(cfg)
	storage := &AWSStorage{
		s3:        client,
		bucket:    aws.String(bucket),
		namespace: namespace,
		uploader:  manager.NewUploader(client), // todo
		//downloader: manager.NewDownloader(client),  // todo
	}
	return storage, nil
}

func (s *AWSStorage) Download(ctx context.Context, key string, writer io.Writer) error {
	key = base.AddNamespace(s.namespace, key)
	out, err := s.s3.GetObject(ctx, &s3.GetObjectInput{
		Bucket: s.bucket,
		Key:    aws.String(key),
	})
	if err != nil {
		return gerrors.Wrap(err)
	}
	if _, err = io.Copy(writer, out.Body); err != nil {
		return gerrors.Wrap(err)
	}
	return nil
}

func (s *AWSStorage) Upload(ctx context.Context, reader io.Reader, key string) error {
	key = base.AddNamespace(s.namespace, key)
	_, err := s.uploader.Upload(ctx, &s3.PutObjectInput{
		Bucket: s.bucket,
		Key:    aws.String(key),
		Body:   reader,
	})
	return gerrors.Wrap(err)
}

func (s *AWSStorage) Delete(ctx context.Context, key string) error {
	key = base.AddNamespace(s.namespace, key)
	_, err := s.s3.DeleteObject(ctx, &s3.DeleteObjectInput{
		Bucket: s.bucket,
		Key:    aws.String(key),
	})
	return gerrors.Wrap(err)
}

func (s *AWSStorage) Rename(ctx context.Context, oldKey, newKey string) error {
	oldKey = base.AddNamespace(s.namespace, oldKey)
	newKey = base.AddNamespace(s.namespace, newKey)
	if oldKey == newKey {
		return nil
	}
	_, err := s.s3.CopyObject(ctx, &s3.CopyObjectInput{
		Bucket:     s.bucket,
		CopySource: aws.String(fmt.Sprintf("%s/%s", *s.bucket, oldKey)),
		Key:        aws.String(newKey),
	})
	if err != nil {
		return gerrors.Wrap(err)
	}
	return gerrors.Wrap(s.Delete(ctx, oldKey))
}

func (s *AWSStorage) CreateSymlink(ctx context.Context, key, symlink string) error {
	key = base.AddNamespace(s.namespace, key)
	_, err := s.s3.PutObject(ctx, &s3.PutObjectInput{
		Bucket: s.bucket,
		Key:    aws.String(key),
		Metadata: map[string]string{
			"symlink": symlink,
		},
	})
	return gerrors.Wrap(err)
}

func (s *AWSStorage) GetMetadata(ctx context.Context, key, tag string) (string, error) {
	key = base.AddNamespace(s.namespace, key)
	out, err := s.s3.HeadObject(ctx, &s3.HeadObjectInput{
		Bucket: s.bucket,
		Key:    aws.String(key),
	})
	if err != nil {
		return "", gerrors.Wrap(err)
	}
	if value, ok := out.Metadata[tag]; ok {
		return value, nil
	}
	return "", gerrors.Wrap(ErrTagNotFound)
}

func (s *AWSStorage) List(ctx context.Context, prefix string) (<-chan *base.StorageObject, <-chan error) {
	prefix = base.AddNamespace(s.namespace, prefix)
	pager := s3.NewListObjectsV2Paginator(s.s3, &s3.ListObjectsV2Input{
		Bucket: s.bucket,
		Prefix: aws.String(prefix),
	})
	ch := make(chan *base.StorageObject)
	errCh := make(chan error, 1)
	go func() {
		defer close(ch)
		defer close(errCh)
		for pager.HasMorePages() {
			page, err := pager.NextPage(ctx)
			if err != nil {
				errCh <- gerrors.Wrap(err)
				return
			}
			for _, obj := range page.Contents {
				key := aws.ToString(obj.Key)
				symlink := ""
				if obj.Size == 0 {
					var err error
					symlink, err = s.GetMetadata(ctx, key, "symlink")
					if err != nil && !errors.Is(err, ErrTagNotFound) {
						errCh <- gerrors.Wrap(err)
						return
					}
				}
				ch <- &base.StorageObject{
					Key:     strings.TrimPrefix(key, prefix),
					Size:    obj.Size,
					ModTime: *obj.LastModified,
					Symlink: symlink,
				}
			}
		}
	}()
	return ch, errCh
}

func getBucketRegion(ctx context.Context, bucket string) (string, error) {
	cfg, err := config.LoadDefaultConfig(context.TODO(), config.WithRegion("us-east-1"))
	if err != nil {
		return "", gerrors.Wrap(err)
	}
	s3Client := s3.NewFromConfig(cfg)
	input := &s3.GetBucketLocationInput{
		Bucket: aws.String(bucket),
	}
	result, err := s3Client.GetBucketLocation(ctx, input)
	if err != nil {
		return "", err
	}
	// AWS S3 returns a location constraint that corresponds to the region.
	// If the constraint is empty, the bucket is in the default region.
	// See: https://docs.aws.amazon.com/AmazonS3/latest/dev/LocationSelection.html
	if result.LocationConstraint == "" {
		return "us-east-1", nil // Default region
	}

	return (string)(result.LocationConstraint), nil
}
