import result as result
import wikipediaapi
import re
from flask import flash, render_template

from forms import AddPageForm

wiki_wiki = wikipediaapi.Wikipedia('ru', timeout=120.0)
# # page_pi = wiki_wiki.page('Питон')
# page_gi = wiki_wiki.page('Гитлер')
#
# print("Page - Title: %s" % page_gi.title)
# print("Page - Summary: %s" % page_gi.summary[0:60])


class Searcher():
    values = dict()

    def __init__(self, start: str, goal: str):
        self.start = start
        self.goal = goal
        Searcher.values.update(first_value=self.start)

    def show_result(self):
        def title_and_link(title: str):
            print(title)
            print(Searcher.values)
            page_py = wiki_wiki.page(title)
            try:
                url = page_py.canonicalurl
            except KeyError:
                url = "Ссылка удалена..."
            return f"\n\"{title}\", ссылка \"{url}\""

        if Searcher.values.get("fourth_value"):
            return_message = f"""
            Мы начали с \"{Searcher.values.get("first_value")}\", и перешли сюда \"{Searcher.values.get("second_value")}\" \n
            Потом нашли это \"{Searcher.values.get("third_value")}\" \n\nА заключающим шагом был он \"{Searcher.values.get("fourth_value")}\" \n
            Вот все линки для пруфов: {title_and_link(Searcher.values.get("first_value"))} -> 
            {title_and_link(Searcher.values.get("second_value"))} ->
            {title_and_link(Searcher.values.get("third_value"))} ->
            {title_and_link(Searcher.values.get("fourth_value"))}.
            """
        elif Searcher.values.get("third_value"):
            return_message = f"""
            Мы начали с \"{Searcher.values.get("first_value")}\", потом перешли сюда \"{Searcher.values.get("second_value")}\" \n
            И закончили тут \"{Searcher.values.get("third_value")}\" \n\n
            Вот все линки для пруфов: {title_and_link(Searcher.values.get("first_value"))}\" -> 
            {title_and_link(Searcher.values.get("second_value"))} ->
            {title_and_link(Searcher.values.get("third_value"))}.
            """
        elif Searcher.values.get("second_value"):
            return_message = f"""
            Мы начали с \"{Searcher.values.get("first_value")}\", а закончили тут \"{Searcher.values.get("second_value")}\" \n\n
            Вот все линки для пруфов: {title_and_link(Searcher.values.get("first_value"))} -> 
            {title_and_link(Searcher.values.get("second_value"))}.
            """
        elif Searcher.values.get("first_value") == self.goal:
            return_message = f"""
            Будь внимательнее. Начало было тут {title_and_link(Searcher.values.get('first_value'))}, 
            и конец тоже тут {title_and_link(Searcher.values.get('first_value'))}.
            """
        else:
            return_message = ''

        Searcher.values = dict()
        print(return_message)
        return Searcher.flasher(return_message)

    def search(self):
        if self.start == self.goal:
            return self.show_result()
        title = self.start
        page = wiki_wiki.page(title)
        links = page.links
        titles = set(links.keys())
        for title in titles:
            Searcher.values.update(second_value=title)
            result = self.is_leads_to_goal(title, self.goal)
            if result:
                # Searcher.values.update(second_value=title)
                return self.show_result()

        for title in titles:
            Searcher.values.update(second_value=title)
            result = self.check_links_page_links(title)
            if type(result) is str and result != "break":
                return self.show_result()
            # break the iteration on success
            elif result == "break":
                break
            else:
                continue

    def check_links_page_links(self, title: str):
        page = wiki_wiki.page(title)
        links = page.links
        titles = set(links.keys())
        for title in titles:
            Searcher.values.update(third_value=title)
            result = self.is_leads_to_goal(title, self.goal)
            if result:
                return title
        for title in titles:
            Searcher.values.update(third_value=title)
            result = self.check_page_links(title)
            if result:
                self.show_result()
                return "break"
        return False

    def check_page_links(self, origin_title: str):
        page = wiki_wiki.page(origin_title)
        links = page.links
        titles = set(links.keys())
        for title in titles:
            result = self.is_leads_to_goal(title, self.goal)
            if result:
                Searcher.values.update(fourth_value=title)
                return title
        return False

    @staticmethod
    def is_leads_to_goal(title: str, goal: str) -> bool:
        result = re.search(rf"(^|\b){goal}(,|\b)", title, flags=re.IGNORECASE)
        return bool(result)

    @staticmethod
    def flasher(message: str):
        flash(message)
        return render_template("findhi.html", form=AddPageForm())

