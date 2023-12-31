import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';

import {
    Button,
    Container,
    ContentLayout,
    DetailsHeader,
    Header,
    ListEmptyMessage,
    Loader,
    Pagination,
    SpaceBetween,
    Table,
    TextFilter,
} from 'components';

import { useBreadcrumbs, useNotifications } from 'hooks';
import { useCollection } from 'hooks';
import { getRepoDisplayName } from 'libs/repo';
import { ROUTES } from 'routes';
import { useGetProjectRepoQuery } from 'services/project';
import { useDeleteSecretMutation, useGetSecretsQuery } from 'services/secret';

import { RepositoryGeneralInfo } from '../components/GeneralInfo';
import { SecretForm } from './SecretForm';

import styles from './styles.module.scss';

export const RepositorySettings: React.FC = () => {
    const { t } = useTranslation();
    const [pushNotification] = useNotifications();
    const params = useParams();
    const paramProjectName = params.name ?? '';
    const paramRepoId = params.repoId ?? '';
    const [isVisibleForm, setIsVisibleForm] = useState(false);
    const [editableSecret, setEditableSecret] = useState<ISecret | undefined>();

    const { data: repoData, isLoading: isLoadingRepo } = useGetProjectRepoQuery({
        name: paramProjectName,
        repo_id: paramRepoId,
    });

    const { data, isLoading } = useGetSecretsQuery({
        project_name: paramProjectName,
        repo_id: paramRepoId,
    });

    const [deleteSecret, { isLoading: isDeleting }] = useDeleteSecretMutation();

    const displayRepoName = repoData ? getRepoDisplayName(repoData) : 'Loading...';

    useBreadcrumbs([
        {
            text: t('navigation.projects'),
            href: ROUTES.PROJECT.LIST,
        },
        {
            text: paramProjectName,
            href: ROUTES.PROJECT.DETAILS.REPOSITORIES.FORMAT(paramProjectName),
        },
        {
            text: t('projects.repositories'),
            href: ROUTES.PROJECT.DETAILS.REPOSITORIES.FORMAT(paramProjectName),
        },
        {
            text: displayRepoName,
            href: ROUTES.PROJECT.DETAILS.REPOSITORIES.DETAILS.FORMAT(paramProjectName, paramRepoId),
        },
        {
            text: t('common.settings'),
            href: ROUTES.PROJECT.DETAILS.REPOSITORIES.SETTINGS.FORMAT(paramProjectName, paramRepoId),
        },
    ]);

    const remove = (secret_name: ISecret['secret_name']) => {
        deleteSecret({
            project_name: paramProjectName,
            repo_id: paramRepoId,
            secret_name: secret_name,
        })
            .unwrap()
            .catch((error) => {
                pushNotification({
                    type: 'error',
                    content: t('common.server_error', { error: error.msg }),
                });
            });
    };

    const edit = (secretName: ISecret['secret_name']) => {
        setEditableSecret({ secret_name: secretName });
        setIsVisibleForm(true);
    };

    const COLUMN_DEFINITIONS = [
        {
            id: 'secret_name',
            header: t('projects.repo.secrets.name'),
            cell: (name: ISecret['secret_name']) => name,
        },
        {
            id: 'secret_value',
            header: `${t('projects.repo.secrets.value')}`,
            cell: (name: ISecret['secret_name']) => (
                <div className={styles.secretValueWrapper}>
                    <div className={styles.secretValue}>************************************</div>
                    <Button disabled={isDeleting} formAction="none" onClick={() => edit(name)} variant="icon" iconName="edit" />

                    <Button
                        disabled={isDeleting}
                        formAction="none"
                        onClick={() => remove(name)}
                        variant="icon"
                        iconName="remove"
                    />
                </div>
            ),
        },
    ];

    const renderEmptyMessage = (): React.ReactNode => {
        return (
            <ListEmptyMessage
                title={t('projects.repo.secrets.empty_message_title')}
                message={t('projects.repo.secrets.empty_message_text')}
            />
        );
    };

    const renderNoMatchMessage = (onClearFilter: () => void): React.ReactNode => {
        return (
            <ListEmptyMessage title={t('common.nomatch_message_title')} message={t('common.nomatch_message_text')}>
                <Button onClick={onClearFilter}>{t('common.clearFilter')}</Button>
            </ListEmptyMessage>
        );
    };

    const { items, actions, filteredItemsCount, collectionProps, filterProps, paginationProps } = useCollection(data ?? [], {
        filtering: {
            empty: renderEmptyMessage(),
            noMatch: renderNoMatchMessage(() => actions.setFiltering('')),
        },
        pagination: { pageSize: 20 },
        selection: {},
    });

    const onCloseForm = () => {
        setIsVisibleForm(false);
        setEditableSecret(undefined);
    };

    return (
        <ContentLayout header={<DetailsHeader title={`${displayRepoName}`} />}>
            <SpaceBetween size="l">
                {isLoadingRepo && !repoData && (
                    <Container>
                        <Loader />
                    </Container>
                )}

                {repoData && <RepositoryGeneralInfo {...repoData} />}

                <Table
                    {...collectionProps}
                    columnDefinitions={COLUMN_DEFINITIONS}
                    items={items}
                    loading={isLoading}
                    loadingText={t('common.loading')}
                    // selectionType="multi"
                    header={
                        <Header
                            actions={
                                <SpaceBetween size="xs" direction="horizontal">
                                    <Button onClick={() => setIsVisibleForm(true)} formAction="none">
                                        {t('common.add')}
                                    </Button>
                                </SpaceBetween>
                            }
                        >
                            {t('projects.repo.secrets.table_title')}
                        </Header>
                    }
                    filter={
                        <TextFilter
                            {...filterProps}
                            filteringPlaceholder={t('projects.repo.secrets.search_placeholder')}
                            countText={t('common.match_count_with_value', { count: filteredItemsCount })}
                            disabled={isLoading}
                        />
                    }
                    pagination={<Pagination {...paginationProps} disabled={isLoading} />}
                />
            </SpaceBetween>

            {isVisibleForm && (
                <SecretForm
                    projectName={paramProjectName}
                    repoId={paramRepoId}
                    onClose={onCloseForm}
                    initialValues={editableSecret}
                />
            )}
        </ContentLayout>
    );
};
