import requests
import time

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
        'disable_notification': True,
        'disable_web_page_preview': True
    }
    response = requests.post(url, data=payload)
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")
    return response

def get_all_branches(repo_owner, repo_name, github_token=None):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/branches"
    headers = {
        'Authorization': f'token {github_token}'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return [branch['name'] for branch in response.json()]
    else:
        print(f"Failed to retrieve branches: {response.status_code}")
        print(response.json())
        return []

def get_latest_commit(repo_owner, repo_name, branch, github_token):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    params = {
        "sha": branch,
        "per_page": 1
    }
    headers = {
        'Authorization': f'token {github_token}'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()[0]
    else:
        print(f"Failed to retrieve commits: {response.status_code}")
        print(response.json())
        return None

def track_commits(repo_owner, repo_name, bot_token=None, chat_id=None, github_token=None):
    branch_commits = {}

    while True:
        try:
            branches = get_all_branches(repo_owner, repo_name, github_token)

            for branch in branches:
                latest_commit = get_latest_commit(repo_owner, repo_name, branch, github_token)

                if latest_commit:
                    if branch not in branch_commits or latest_commit['sha'] != branch_commits[branch]:
                        branch_commits[branch] = latest_commit['sha']

                        author_name = latest_commit['commit']['author']['name']
                        author_login = latest_commit['author']['login'] if latest_commit.get('author') else None
                        author_profile_url = f"https://github.com/{author_login}" if author_login else "N/A"
                        message = (
                            f"<b>New Commit detected</b>\n"
                            f"<b>------------------------</b>\n"
                            f"<b>Repository : </b> \n"
                            f"<a href='https://github.com/{repo_owner}/{repo_name}'>{repo_name}</a>\n"
                            f"\n"
                            f"<b>Branch :</b> <code>{branch}</code>\n"
                            f"\n"
                            f"<b>Commit : </b>\n"
                            f"<code>{latest_commit['sha']}</code>\n"
                            f"\n"
                            f"<b>Author :</b> <a href='{author_profile_url}'>{author_name}</a>\n"
                            f"\n"
                            f"<b>Message : </b>\n"
                            f"<code>{latest_commit['commit']['message'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}</code>\n"
                        )
                        print(message)

                        if bot_token and chat_id:
                            response = send_telegram_message(bot_token, chat_id, message)
                            if response.status_code != 200:
                                print(f"Failed to send message: {response.status_code}")

            time.sleep(60)
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(5)

repo_owner = "change_this"
repo_name = "change_this"
bot_token = "change_this"
chat_id = "change_this"
github_token = "change_this"

track_commits(repo_owner, repo_name, bot_token, chat_id, github_token)
