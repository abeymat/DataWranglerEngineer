# Known Limitations

- CSV is the only implemented extraction format.
- The approved transformation graph currently targets the customer-to-Salesforce Account demo
  contract; GPT-5.6 cannot synthesize arbitrary executable workflows.
- Salesforce load means validated CSV/load-contract preparation, not direct org mutation.
- Workflow persistence, rerun history, and the bounded repair agent are not implemented yet.
- The worker process provides timeout and process separation but is not a hardened OS sandbox.
- GPT-5.6 planning requires an OpenAI project with model access and incurs API usage. The local
  fallback is intentionally labeled and is not represented as a model call.
- `store=false` and payload minimization are implemented, but the app does not claim Zero Data
  Retention or comprehensive sensitive-data classification.
- Automatic tests mock OpenAI. A live GPT-5.6 smoke test must be run separately with authorized
  credentials before recording the demo.
- The UI previews output but does not yet provide a final downloadable CSV button.
