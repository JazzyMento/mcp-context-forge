# Helm Chart Validation Security Assessment

This document records security and test-environment risks identified during the MCP Gateway Helm chart validation project.

The scope of this assessment is the automated Helm chart validation workflow, including the Kind test environment, Helm values, Kubernetes test resources, CI pipeline (helm-chart-validation-ci), security scanning and runtime evidence collection. It is NOT a full production security assessment of the entire MCP Gateway platform.

This document and table below shows risk-based decision making: I identified potential threats in the validation workflow, judged likelihood versus impact, and took appropriate action / documented the production requirement.



## Threat assessment

| Threat                                               |                       Likelihood |      Impact | Action taken / rationale                                                                                                                                        | Documented                                                                        |
| ---------------------------------------------------- | -------------------------------: | ----------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Test credentials accidentally reused in production   |                           Medium |        High | Marked `values-kind-test.yaml` as test-only and not for production. Production should use strong secrets from Kubernetes Secrets or external secret management | `values-kind-test.yaml` comments and placeholder secret section                 |
| Hardcoded or weak secrets                            |                           Medium |        High | Used placeholders (matching `values.yaml`) such as `changeme`, `my-test-key` and `my-test-salt` only in the temporary validation profile. These values are acceptable for a disposable test environment but not for production                            | `values-kind-test.yaml`, security write-up                                      |
| Unencrypted data in transit                          | Low in Kind / High in production |        High | In the Kind validation workflow, Helm test pods call the gateway through internal Kubernetes service DNS. This is acceptable for an isolated non-production test environment with no production data. In production, gateway traffic should use TLS/HTTPS through ingress or encryption                                      | `gateway-health-test.yaml`, ingress disabled in Kind values, notes in `docs/helm-chart-validation-security-assessment.md` |
| Unencrypted data at rest                             | Low in Kind / High in production |        High | Documented in the security assessment and Kind values comments that the Kind environment is temporary, non-production and does not hold production data. In production, Postgres persistent storage should use encrypted volumes or platform-managed encryption because production databases may contain sensitive configuration, tokens or operational data | `charts/mcp-stack/values-kind-test.yaml` Postgres values, notes in `docs/helm-chart-validation-security-assessment.md`   |
| Auth/JWT/registration flows can affect optional registration jobs                       |                           Medium |        High |Disabled optional auto-registration flows in the Kind test profile to keep chart validation focused on deployment, gateway health and dependency discovery. Full auth/RBAC registration testing is outside this chart validation scope. Production deployments should enforce authentication and access control                       | `values-kind-test.yaml`, registration settings                                  |
| Python code security issue                           |                           Medium | Medium/High | Added a Bandit security scan through the security-check Makefile target and included this in the GitHub Actions so common Python security risks are checked on every push                                                                                                  | `make security-check`,  Run security checks in CI, Bandit output                          |
| ServiceMonitor CRD failure in lightweight CI cluster |                           Medium |      Medium | Disabled ServiceMonitor in Kind values because CI does not install Prometheus Operator CRDs. This prevents unrelated CRD failures during chart validation                                                                  | `values-kind-test.yaml` ServiceMonitor disabled                |
| Monitoring data (CPU / memory metrics) may be unavailable in a temporary Kind cluster                    |                           Medium |  Low/Medium | Installed metrics-server and made runtime snapshot collection tolerant of unavailable metrics. This keeps monitoring evidence useful without allowing metrics collection to block chart validation                                                                 | `test_kind.sh`, runtime snapshot artefacts                                      |



## Data in transit

The Kind validation workflow uses internal Kubernetes service traffic only. The Helm test pod calls the MCP Gateway service through in-cluster service DNS using the `/health` endpoint. This is used to validate that the gateway service is reachable after deployment.

This is acceptable for the temporary Kind validation environment because the cluster is isolated, non-production and does not process production data. The health check does not transmit production data or user data.

This does not prove that production traffic is encrypted. In a production deployment, MCP Gateway traffic should be protected using TLS/HTTPS through ingress or an equivalent platform control. Production deployments should also enforce authentication and access control, and sensitive values should be managed through Kubernetes Secrets or an approved external secret manager.


## Data at rest

The Kind validation environment is temporary and is used only for Helm chart testing; it does not process or store production data. Any Postgres data created during the Kind test is test data only and is discarded when the temporary Kind cluster is deleted.

Because it is a temporart Kind cluster that is deleted after the test run, production-grade encrypted persistent storage is not required for the Kind validation workflow itself. However, this does not prove that production storage is secure. In a production deployment, Postgres persistent volumes should use encrypted storage, such as cloud-provider encrypted disks or platform-managed volume encryption, because production databases may contain sensitive configuration, tokens, credentials or operational data.
