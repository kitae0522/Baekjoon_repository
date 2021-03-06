import os
from bs4 import BeautifulSoup
import requests as req
import pandas as pd
import csv
import datetime

solved_problems_DB = pd.read_csv('solved_problems.csv')

SECONDS_IN_A_DAY = 60*60*24
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.99 Safari/537.36"
}
data_set = {}
file_name_extension = {}


class AutoBoj:

    __VERSION__ = '1.0.2'

    def __init__(self, configure_obj):
        self.git_name = configure_obj["git_name"]
        self.git_email = configure_obj["git_email"]
        self.git_repo = configure_obj["git_repo"]
        self.boj_name = configure_obj["boj_name"]

    def set_up_git(self):
        script = [f'git config --global user.name "{self.git_name}"',
                  f'git config --global user.email "{self.git_email}"',
                  f'git add .',
                  'cls']
        for i in script:
            os.system(i)

    def check_file(self):
        path_dir = os.path.dirname(os.path.realpath(__file__))
        file_list = os.listdir(path_dir + "/boj/")
        for i in file_list:
            try:
                solved_problems_DB.loc[0, os.path.splitext(i)[0][4:]]
                file_name_extension[os.path.splitext(i)[0]] = "c" if os.path.splitext(i)[1] == ".c" else "cpp" if os.path.splitext(i)[1] == ".cpp" else "py" if os.path.splitext(i)[
                    1] == ".py" else "java" if os.path.splitext(i)[1] == ".java" else "go" if os.path.splitext(i)[1] == ".go" else "txt" if os.path.splitext(i)[1] == ".txt" else"None"
            except KeyError:
                continue

    def crawl_user_data(self):
        print("Please wait. Started Crawling...")
        url = f"https://www.acmicpc.net/user/{self.boj_name}"
        html = req.get(url, headers=headers)
        soup = BeautifulSoup(html.content, 'html.parser')
        li = soup.find("div", {"class": "panel-body"}).find_all("a")

        def load_data_status(problem_id):
            url = f"https://www.acmicpc.net/status?problem_id={problem_id}&user_id={self.boj_name}"
            html = req.get(url, headers=headers)
            soup = BeautifulSoup(html.content, 'html.parser')
            table = soup.find(
                "table", {"class": "table table-striped table-bordered"}).findAll("tbody")
            for i in table:
                problem_title = i.find(
                    "a", {"class": "problem_title"}).attrs["title"]
                data_original_title = i.find(
                    "a", {"class": "real-time-update"}).attrs["title"]
                li = data_original_title.split()
                [li.pop() for _ in range(3)]
                datetime_object = datetime.datetime.strptime(
                    " ".join(li), "%Y년 %m월 %d일")
                date_title = datetime_object.strftime("%y-%m-%d")
                return [problem_title, date_title]

        for i in range(len(li)):
            problem_number = li[i].text
            try:
                data_set[problem_number] = [solved_problems_DB.loc[0,
                                                                   problem_number], solved_problems_DB.loc[1, problem_number]]
            except KeyError:
                print(f"{i+1}/{len(li)+1}")
                status = load_data_status(problem_number)
                problem_title, data_original_title = status[0], status[1]
                data_set[problem_number] = [problem_title, data_original_title]
        df = pd.DataFrame.from_dict(data_set)
        df.to_csv("solved_problems.csv")

    def write_markdown(self):
        li = []
        with open("BOJ.md", "w", encoding="UTF8") as file:
            title = f"""|No|Title|Solution Link|Problem Link|Last Solve|\n| :--: | :--: | :--: | :--: | :--: |\n"""
            file.write(title)
            index = 1
            for number in data_set:
                try:
                    extension = "c" if file_name_extension["boj_"+number] == "c" else "cpp" if file_name_extension["boj_"+number] == "cpp" else "py" if file_name_extension["boj_" +
                                                                                                                                                                            number] == "py" else "java" if file_name_extension["boj_"+number] == "java" else "go" if file_name_extension["boj_"+number] == "go" else "txt" if file_name_extension["boj_"+number] == "txt" else "None"
                except KeyError:
                    print(
                        f"error: No.{number} File not found.\nPlease download the code from http://boj.kr/{number}.")
                    continue
                li.append(
                    f"""|{number}|**{data_set[number][0]}**|[/boj/boj_{number}.{extension}]({self.git_repo}/blob/master/boj/boj_{number}.{extension})|[http://boj.kr/{number}](https://www.acmicpc.net/problem/{number})|{data_set[number][1]}|\n""")
            for i in li:
                file.write(i)

    def commit(self):
        print("If you want commit?(Y/N)")
        cmd = input("> ")
        if cmd == "Y" or cmd == "y" or cmd == "Yes" or cmd == "yes":
            script = ['git pull', 'git add --all',
                      f'git commit -m "{commit_message}"', 'git push origin', 'cls']
            for i in script:
                os.system(i)
            print("Complete. Relaunching...")
        elif cmd == "N" or cmd == "n" or cmd == "No" or cmd == "no":
            print("Ok.")
        os.system(f"TIMEOUT {SECONDS_IN_A_DAY}")
        AutoBoj.check_file(self)
        AutoBoj.crawl_user_data(self)
        AutoBoj.write_markdown(self)
        AutoBoj.commit(self)


if __name__ == "__main__":
    """
    if there is a commit message you want,
    please correct it here.
    """
    commit_message = "update"

    """
    And these are the things you need to set up.
    example:
        # git_name = "kitae0522"
        # git_email = "kitae0522@naver.com"
        # git_repo = "https://github.com/kitae0522/test"
        # boj_name = "kitae0522"
    """
    ab = AutoBoj({"git_name": "kitae0522",
                  "git_email": "kitae0522@naver.com",
                  "git_repo": "https://github.com/kitae0522/Online-Problem-Solving",
                  "boj_name": "kitae0522"})
    print(ab.__VERSION__)
    ab.set_up_git()
    ab.check_file()
    ab.crawl_user_data()
    ab.write_markdown()
    ab.commit()
