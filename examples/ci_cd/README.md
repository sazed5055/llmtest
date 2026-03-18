# CI/CD Integration Examples for llmtest

This directory contains example configurations for integrating llmtest into your CI/CD pipelines.

## GitHub Actions

**File:** `github_actions.yml`

**Setup:**
1. Copy `github_actions.yml` to `.github/workflows/llm-tests.yml` in your repository
2. Add your API key as a GitHub secret:
   - Go to Settings → Secrets and variables → Actions
   - Add `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
3. Push to trigger the workflow

**Features:**
- ✅ Run tests on every push and PR
- ✅ Daily scheduled test runs
- ✅ Regression comparison on PRs
- ✅ HTML and JSON report artifacts
- ✅ PR comments with test results
- ✅ Cost tracking on main branch

**Workflow Jobs:**
1. **llm-tests** - Run full test suite
2. **regression-tests** - Compare PR changes to main branch
3. **cost-tracking** - Track API usage metrics

---

## GitLab CI

**File:** `gitlab_ci.yml` (coming soon)

---

## Jenkins

**File:** `Jenkinsfile` (coming soon)

---

## Local Testing Before CI

Test your configuration locally before pushing:

```bash
# Install llmtest
pip install 'git+https://github.com/sazed5055/llmtest.git@v0.1.0#egg=llmtest[all]'

# Set API key
export OPENAI_API_KEY='your-key'

# Run tests
llmtest run tests/llmtest.yaml --output results.json

# Generate HTML report
llmtest run tests/llmtest.yaml --html report.html
```

---

## Best Practices

### 1. **Use Secrets for API Keys**
Never commit API keys to your repository. Use your CI platform's secrets management:
- GitHub: Secrets and variables
- GitLab: CI/CD Variables
- Jenkins: Credentials

### 2. **Cost Management**
LLM API calls can be expensive. Consider:
- Run tests only on important branches
- Use scheduled runs instead of every commit
- Set up cost alerts in your cloud provider
- Use cheaper models for non-critical tests (gpt-4o-mini vs gpt-4o)

### 3. **Caching**
Cache test results to avoid redundant API calls:
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.llmtest-cache
    key: llm-tests-${{ hashFiles('tests/**') }}
```

### 4. **Parallel Execution**
Speed up tests by running in parallel:
```bash
llmtest run tests/ --parallel --workers 4
```

### 5. **Fail Fast**
Configure tests to fail fast on critical issues:
```yaml
- name: Run critical tests first
  run: llmtest run tests/critical/ --fail-fast
```

---

## Monitoring and Alerts

### Set up alerts for:
- Test failures
- Regression detection
- API cost spikes
- Response time degradation

### Example Slack notification:
```yaml
- name: Notify Slack on failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "❌ LLM tests failed in ${{ github.repository }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Troubleshooting

### Common Issues:

**1. API Key Not Found**
```
Error: OPENAI_API_KEY environment variable not set
```
**Solution:** Add API key to CI secrets

**2. Rate Limiting**
```
Error: Rate limit exceeded
```
**Solution:** Add retry logic or reduce test frequency

**3. Timeout**
```
Error: Test timeout after 10 minutes
```
**Solution:** Increase timeout or optimize tests:
```yaml
timeout-minutes: 30
```

**4. Cost Concerns**
**Solution:** Use mock provider for non-critical tests:
```yaml
provider: mock  # Free, no API calls
```

---

## Example Project Structure

```
your-repo/
├── .github/
│   └── workflows/
│       └── llm-tests.yml
├── tests/
│   ├── llmtest.yaml          # Test configuration
│   └── critical/
│       └── safety-tests.yaml
├── .env.example              # Example environment variables
└── README.md
```

---

## Contributing

Have CI/CD examples for other platforms? PRs welcome!
- CircleCI
- Azure DevOps
- Bitbucket Pipelines
- Travis CI
