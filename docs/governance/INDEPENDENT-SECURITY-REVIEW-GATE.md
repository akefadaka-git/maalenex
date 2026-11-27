# Independent External Security Review Gate

**Status:** Mandatory repository governance policy  
**Authority:** Owner direction  
**Scope:** MaaleNex development, release, and deployment lifecycle

## 1. Binding rule

A qualified independent external security review is a mandatory **pre-deployment gate**. It is not a routine requirement for every development stage, pull request, remediation cycle, or A1–A4 activity.

## 2. Development-stage rule

During ordinary development and A1–A4 work:

- Do not request, schedule, or require an independent external security reviewer solely to complete a development stage or close an ordinary development finding.
- Do not ask the Owner to nominate an external reviewer during routine development.
- Continue internal engineering review, automated security checks, testing, remediation, and evidence collection according to the applicable stage scope.
- Record security findings and unresolved risks accurately. A finding may remain open or accepted for a documented development-stage disposition where permitted by the applicable stage criteria; this does not authorize deployment.

## 3. Pre-deployment gate

Before any production deployment is proposed or authorized:

1. Arrange a qualified reviewer who is independent of the implementation work.
2. Provide the reviewer the release candidate, relevant source and configuration, threat model, security-sensitive changes, test evidence, and known findings.
3. Obtain and record the review report, reviewer identity and qualifications, reviewed commit SHA, findings, severity, and remediation or formal risk disposition.
4. Resolve or explicitly disposition findings under Owner governance and applicable release policy.
5. Verify that the reviewed commit is the exact release candidate. Material changes after review require impact assessment and, where relevant, re-review.
6. Present the complete evidence and outstanding risks to the Owner for the separate deployment decision.

No deployment may proceed without this gate and explicit deployment authorization.

## 4. No implied deployment readiness

Completion of A1–A4, passing CI, internal security review, or closure of development findings does not itself mean deployment is imminent, approved, or authorized. Deployment remains a separate stage and requires a separate explicit Owner decision.

## 5. Communication and escalation

The assistant and contributors must not repeatedly ask the Owner for an external reviewer during development. Raise the reviewer-selection question only when a concrete pre-deployment review is being prepared, and only if the Owner has not already designated the reviewer or review provider.

Do not describe an ordinary development-stage review as a deployment gate or make external review an added prerequisite to unrelated development-stage closure.

## 6. Change control

This policy records an Owner governance instruction. It may be changed only through explicit Owner approval and a traceable repository change.