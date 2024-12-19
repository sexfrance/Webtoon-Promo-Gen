<div align="center">
  <h2 align="center">Webtoon Promo Generator</h2>
  <p align="center">
This script is an asynchronous Webtoon account and discord promo code generator that features proxy support, RSA encryption, and efficient batch processing. It automatically creates Webtoon accounts, generates discord promotion codes, validates the entire process, and provides formatted output.

The code is not like my other repos because it was made only for me. You can get cancer reading the code (I will not pay for your chemotherapy), and there are no configs. 
    <br />
    <br />
    <a href="https://discord.cyberious.xyz">💬 Discord</a>
    ·
    <a href="https://github.com/sexfrance/Webtoon-Promo-Gen#-changelog">📜 ChangeLog</a>
    ·
    <a href="https://github.com/sexfrance/Webtoon-Promo-Gen/issues">⚠️ Report Bug</a>
    ·
    <a href="https://github.com/sexfrance/Webtoon-Promo-Gen/issues">💡 Request Feature</a>
  </p>
</div>

### ⚙️ Installation

- Requires: `Python 3.7+`
- Make a python virtual environment: `python3 -m venv venv`
- Source the environment: `venv\Scripts\activate` (Windows) / `source venv/bin/activate` (macOS, Linux)
- Install the requirements: `pip install -r requirements.txt`

---

### 🔥 Features

- Creates Webtoon accounts automatically with random or custom credentials
- Generates discord promotion codes for each created account
- Supports both proxy and proxyless modes
- Logs results with different levels (success, failure)
- Generates random valid email addresses and secure passwords
- Saves both account credentials and discord promotion codes to separate files
- Efficient batch processing for multiple accounts/codes generation

---

### 📝 Usage

- (Optional) Prepare a file named `proxies.txt` with proxies, one per line in user:pass@ip:port format, if you want to use proxies.

- (Optional) You can edit the DEBUG variable in the main script to display detailed information.

- Run the script:

  ```sh
  python main.py
  ```

- The script will generate three files:
  - `accounts.txt` - Contains the created accounts in email:password format
  - `promos.txt` - Contains the generated discord promotion codes
  - `full_account_capture.txt` - Contains the full account capture (account + email login) username:email:password:token format

---

### 📹 Preview

**❗ I don't have a preview for this since they stopped the promotion but here is the account generator it looks the same there are just more steps**

![Preview](https://i.imgur.com/qPJpXTs.gif)

---

### ❗ Disclaimers

- This project is for education purposes **only** its goal is to understand webtoons' API better. I strongly suggest that you not use it to mass generate accounts and promos because it is against their [**terms of service**](https://www.webtoons.com/en/terms).
- I am not responsible for anything that may happen, such as API Blocking, IP ban, etc.
- This was a quick project that was made for fun and personal use if you want to see further updates, star the repo & create an "issue" [here](https://github.com/sexfrance/Webtoon-Promo-Gen/issues/)

---

### 📜 ChangeLog

```diff
v0.0.1 ⋮ 12/07/2024
! Initial release with discord promotion code generation feature
```

---

<p align="center">
  <img src="https://img.shields.io/github/license/sexfrance/Webtoon-Account-Creator.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=IOTA"/>
  <img src="https://img.shields.io/github/stars/sexfrance/Webtoon-Account-Creator.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=IOTA"/>
  <img src="https://img.shields.io/github/languages/top/sexfrance/Webtoon-Account-Creator.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=python"/>
</p>
