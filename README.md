# Streamlabs Account Checker

A powerful and efficient multi-threaded Streamlabs account checker built using Python with support for proxies, logging, and robust error handling.

## Features
✅ Multi-threaded for fast performance
✅ Proxy support for anonymity and avoiding bans
✅ Detailed logging with categorized console outputs
✅ Automatically removes checked accounts
✅ Captures linked platforms for valid accounts
✅ Error handling with retry logic for failed attempts

## Requirements
- Python 3.11 or higher
- `tls_client` for secure TLS session management
- `console.py` for detailed and color-coded logs

## Installation
1. Clone this repository:
```bash
git clone https://github.com/Payloadop/Streamlabs-Account-Checker.git
cd streamlabs-checker
```
2. Install the required dependencies:
```bash
pip install tls-client
```

## Configuration

1. Add your accounts to `accs.txt` in the format:
```
email1@example.com:password123
email2@example.com:password456
```

2. Add your proxies to `proxies.txt` (one per line):
```
username:password@ip:port
username:password@ip:port
```

## Usage
To run the checker:
```bash
python main.py
```

## How It Works
1. The script loads accounts from `accs.txt`.
2. For each account:
   - A TLS client is created using `tls_client`.
   - The client retrieves the XSRF token and logs in.
   - If successful, the linked platforms are extracted and saved to `valid.txt`.
   - If invalid, the account is saved to `invalid.txt`.
3. Threads are used to process multiple accounts simultaneously.

## Output
- **Valid Accounts:** Stored in `valid.txt` with format: `email:password:linked_platforms`
- **Invalid Accounts:** Stored in `invalid.txt`
- **Console Logging:** Provides success, error, and warning messages in real-time

## Example Console Output
```
[info] Loaded 100 accounts. Running on 50 threads...
[success] [user1@example.com] Successfully Logged In!
[info] [user1@example.com] Saved to valid.txt -> Twitch, YouTube
[error] [user2@example.com] Failed login (Invalid credentials)
```

## Known Issues
- Some proxies may cause frequent retries; ensure your proxy list is clean.
- OAuth flow may sometimes fail if redirects are inconsistent.

## To-Do
- Implement automatic proxy rotation for better stability.
- Add rate-limiting management for improved success rates.

## License
This project is licensed under the MIT License.

## Support
For issues or suggestions, feel free to open an issue or contribute via pull requests. Happy checking! 🚀
Join discord.gg/payloadtheskid
