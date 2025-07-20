# Responses to Questions.

## Question #1 Response:

### Vulnerability #1: .netrc Credentials Leak in requests

- Issue: .netrc credentials may be leaked to third parties if maliciously-crafted URLs are used.
- Current Version in Use: requests==2.32.3
- Vulnerable Versions: < 2.32.4
- Fixed Version: 2.32.4
- Recommended Fix:

```txt
requests>=2.32.4
```

- Workaround for Older Versions:

```python
requests.Session(trust_env=False)
```
    - This disables .netrc usage from environment variables.

### More info resources

Upstream Issue: [psf/requests#6965](https://github.com/psf/requests/pull/6965)

Security Advisory Reference: [Seclists Full Disclosure (June 2025)](https://seclists.org/fulldisclosure/2025/Jun/2)

