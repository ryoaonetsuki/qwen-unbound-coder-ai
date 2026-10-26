# Security notes
- No password, token, cookie, or API key is in this repo. The only key is
  `QWEN_API_KEY`, which you invent in the notebook at runtime and type into
  the frontend on your own phone; it is stored only in that browser's
  localStorage, never in the repo.
- The gateway binds llama-server to 127.0.0.1 only. The tunnel exposes the
  gateway, not llama-server directly. Anyone with the tunnel URL + key can
  chat — treat the URL as semi-private, rotate the key each session, and
  shut the notebook down when done.
- Do not paste Colab/Kaggle/Hugging Face passwords or session cookies
  anywhere in this project, in chat, or in issues.
- "Reduced refusal" describes the published weights. It does not remove your
  responsibility for what you generate or share, and the base model's Apache
  2.0 licence and acceptable-use terms still apply.
