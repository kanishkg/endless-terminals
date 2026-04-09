# test_initial_state.py
"""
Tests to validate the initial state of the filesystem before the student performs
the Kubernetes manifest analysis task.
"""

import os
import pytest


class TestDirectoryStructure:
    """Test that the required directory structure exists."""

    def test_k8s_manifests_base_directory_exists(self):
        """The base k8s-manifests directory must exist."""
        path = "/home/user/k8s-manifests"
        assert os.path.isdir(path), f"Directory {path} does not exist"

    def test_dev_subdirectory_exists(self):
        """The dev subdirectory must exist."""
        path = "/home/user/k8s-manifests/dev"
        assert os.path.isdir(path), f"Directory {path} does not exist"

    def test_staging_subdirectory_exists(self):
        """The staging subdirectory must exist."""
        path = "/home/user/k8s-manifests/staging"
        assert os.path.isdir(path), f"Directory {path} does not exist"

    def test_prod_subdirectory_exists(self):
        """The prod subdirectory must exist."""
        path = "/home/user/k8s-manifests/prod"
        assert os.path.isdir(path), f"Directory {path} does not exist"


class TestDevManifestFiles:
    """Test that dev environment manifest files exist with correct content."""

    def test_dev_app_yaml_exists(self):
        """The dev/app.yaml file must exist."""
        path = "/home/user/k8s-manifests/dev/app.yaml"
        assert os.path.isfile(path), f"File {path} does not exist"

    def test_dev_app_yaml_contains_deployment(self):
        """The dev/app.yaml must contain a Deployment resource."""
        path = "/home/user/k8s-manifests/dev/app.yaml"
        with open(path, 'r') as f:
            content = f.read()
        assert "kind: Deployment" in content, f"File {path} does not contain 'kind: Deployment'"

    def test_dev_app_yaml_contains_service(self):
        """The dev/app.yaml must contain a Service resource."""
        path = "/home/user/k8s-manifests/dev/app.yaml"
        with open(path, 'r') as f:
            content = f.read()
        assert "kind: Service" in content, f"File {path} does not contain 'kind: Service'"

    def test_dev_app_yaml_contains_configmap(self):
        """The dev/app.yaml must contain a ConfigMap resource."""
        path = "/home/user/k8s-manifests/dev/app.yaml"
        with open(path, 'r') as f:
            content = f.read()
        assert "kind: ConfigMap" in content, f"File {path} does not contain 'kind: ConfigMap'"

    def test_dev_database_yaml_exists(self):
        """The dev/database.yaml file must exist."""
        path = "/home/user/k8s-manifests/dev/database.yaml"
        assert os.path.isfile(path), f"File {path} does not exist"

    def test_dev_database_yaml_contains_deployment(self):
        """The dev/database.yaml must contain a Deployment resource."""
        path = "/home/user/k8s-manifests/dev/database.yaml"
        with open(path, 'r') as f:
            content = f.read()
        assert "kind: Deployment" in content, f"File {path} does not contain 'kind: Deployment'"

    def test_dev_database_yaml_contains_secret(self):
        """The dev/database.yaml must contain a Secret resource."""
        path = "/home/user/k8s-manifests/dev/database.yaml"
        with open(path, 'r') as f:
            content = f.read()
        assert "kind: Secret" in content, f"File {path} does not contain 'kind: Secret'"

    def test_dev_database_yaml_contains_service(self):
        """The dev/database.yaml must contain a Service resource."""
        path = "/home/user/k8s-manifests/dev/database.yaml"
        with open(path, 'r') as f:
            content = f.read()
        assert "kind: Service" in content, f"File {path} does not contain 'kind: Service'"


class TestStagingManifestFiles:
    """Test that staging environment manifest files exist with correct content."""

    def test_staging_app_yaml_exists(self):
        """The staging/app.yaml file must exist."""
        path = "/home/user/k8s-manifests/staging/app.yaml"
        assert os.path.isfile(path), f"File {path} does not exist"

    def test_staging_app_yaml_contains_deployment(self):
        """The staging/app.yaml must contain a Deployment resource."""
        path = "/home/user/k8s-manifests/staging/app.yaml"
        with open(path, 'r') as f:
            content = f.read()
        assert "kind: Deployment" in content, f"File {path} does not contain 'kind: Deployment'"

    def test_staging_app_yaml_contains_ingress(self):
        """The staging/app.yaml must contain an Ingress resource."""
        path = "/home/user/k8s-manifests/staging/app.yaml"
        with open(path, 'r') as f:
            content = f.read()
        assert "kind: Ingress" in content, f"File {path} does not contain 'kind: Ingress'"

    def test_staging_monitoring_yaml_exists(self):
        """The staging/monitoring.yaml file must exist."""
        path = "/home/user/k8s-manifests/staging/monitoring.yaml"
        assert os.path.isfile(path), f"File {path} does not exist"

    def test_staging_monitoring_yaml_contains_deployment(self):
        """The staging/monitoring.yaml must contain a Deployment resource."""
        path = "/home/user/k8s-manifests/staging/monitoring.yaml"
        with open(path, 'r') as f:
            content = f.read()
        assert "kind: Deployment" in content, f"File {path} does not contain 'kind: Deployment'"


class TestProdManifestFiles:
    """Test that prod environment manifest files exist with correct content."""

    def test_prod_app_yaml_exists(self):
        """The prod/app.yaml file must exist."""
        path = "/home/user/k8s-manifests/prod/app.yaml"
        assert os.path.isfile(path), f"File {path} does not exist"

    def test_prod_app_yaml_contains_deployment(self):
        """The prod/app.yaml must contain a Deployment resource."""
        path = "/home/user/k8s-manifests/prod/app.yaml"
        with open(path, 'r') as f:
            content = f.read()
        assert "kind: Deployment" in content, f"File {path} does not contain 'kind: Deployment'"

    def test_prod_app_yaml_contains_hpa(self):
        """The prod/app.yaml must contain a HorizontalPodAutoscaler resource."""
        path = "/home/user/k8s-manifests/prod/app.yaml"
        with open(path, 'r') as f:
            content = f.read()
        assert "kind: HorizontalPodAutoscaler" in content, f"File {path} does not contain 'kind: HorizontalPodAutoscaler'"

    def test_prod_app_yaml_contains_ingress(self):
        """The prod/app.yaml must contain an Ingress resource."""
        path = "/home/user/k8s-manifests/prod/app.yaml"
        with open(path, 'r') as f:
            content = f.read()
        assert "kind: Ingress" in content, f"File {path} does not contain 'kind: Ingress'"

    def test_prod_database_yaml_exists(self):
        """The prod/database.yaml file must exist."""
        path = "/home/user/k8s-manifests/prod/database.yaml"
        assert os.path.isfile(path), f"File {path} does not exist"

    def test_prod_database_yaml_contains_deployment(self):
        """The prod/database.yaml must contain a Deployment resource."""
        path = "/home/user/k8s-manifests/prod/database.yaml"
        with open(path, 'r') as f:
            content = f.read()
        assert "kind: Deployment" in content, f"File {path} does not contain 'kind: Deployment'"

    def test_prod_database_yaml_contains_pvc(self):
        """The prod/database.yaml must contain a PersistentVolumeClaim resource."""
        path = "/home/user/k8s-manifests/prod/database.yaml"
        with open(path, 'r') as f:
            content = f.read()
        assert "kind: PersistentVolumeClaim" in content, f"File {path} does not contain 'kind: PersistentVolumeClaim'"

    def test_prod_database_yaml_contains_secret(self):
        """The prod/database.yaml must contain a Secret resource."""
        path = "/home/user/k8s-manifests/prod/database.yaml"
        with open(path, 'r') as f:
            content = f.read()
        assert "kind: Secret" in content, f"File {path} does not contain 'kind: Secret'"


class TestResourceCounts:
    """Test that the expected resource counts are present in the manifest files."""

    def _count_kind_occurrences(self, kind: str) -> int:
        """Count occurrences of a specific kind across all YAML files."""
        count = 0
        base_path = "/home/user/k8s-manifests"
        for root, dirs, files in os.walk(base_path):
            for filename in files:
                if filename.endswith('.yaml') or filename.endswith('.yml'):
                    filepath = os.path.join(root, filename)
                    with open(filepath, 'r') as f:
                        for line in f:
                            if line.strip() == f"kind: {kind}":
                                count += 1
        return count

    def test_deployment_count(self):
        """There should be exactly 6 Deployment resources."""
        count = self._count_kind_occurrences("Deployment")
        assert count == 6, f"Expected 6 Deployment resources, found {count}"

    def test_service_count(self):
        """There should be exactly 6 Service resources."""
        count = self._count_kind_occurrences("Service")
        assert count == 6, f"Expected 6 Service resources, found {count}"

    def test_configmap_count(self):
        """There should be exactly 4 ConfigMap resources."""
        count = self._count_kind_occurrences("ConfigMap")
        assert count == 4, f"Expected 4 ConfigMap resources, found {count}"

    def test_ingress_count(self):
        """There should be exactly 2 Ingress resources."""
        count = self._count_kind_occurrences("Ingress")
        assert count == 2, f"Expected 2 Ingress resources, found {count}"

    def test_secret_count(self):
        """There should be exactly 2 Secret resources."""
        count = self._count_kind_occurrences("Secret")
        assert count == 2, f"Expected 2 Secret resources, found {count}"

    def test_hpa_count(self):
        """There should be exactly 1 HorizontalPodAutoscaler resource."""
        count = self._count_kind_occurrences("HorizontalPodAutoscaler")
        assert count == 1, f"Expected 1 HorizontalPodAutoscaler resource, found {count}"

    def test_pvc_count(self):
        """There should be exactly 1 PersistentVolumeClaim resource."""
        count = self._count_kind_occurrences("PersistentVolumeClaim")
        assert count == 1, f"Expected 1 PersistentVolumeClaim resource, found {count}"


class TestOutputFileDoesNotExist:
    """Ensure the output file does not exist before the task is performed."""

    def test_report_file_does_not_exist(self):
        """The output report file should not exist before the task."""
        path = "/home/user/k8s-manifests/resource-frequency-report.txt"
        assert not os.path.exists(path), f"Output file {path} should not exist before task execution"
