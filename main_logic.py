import result as result
import wikipediaapi
import re
from flask import flash, render_template

from forms import AddPageForm

wiki_wiki = wikipediaapi.Wikipedia('ru')
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

    @classmethod
    def show_result(cls):
        def title_and_link(title: str):
            print(title)
            print(Searcher.values)
            page_py = wiki_wiki.page(title)
            return f"\n\"{title}\", ссылка \"{page_py.canonicalurl}\""

        if cls.values.get("fourth_value"):
            return_message = f"""
            Мы начали с \"{cls.values.get("first_value")}\", и перешли сюда \"{cls.values.get("second_value")}\" \n
            Потом нашли это \"{cls.values.get("third_value")}\" \n\nА заключающим шагом был он \"{cls.values.get("fourth_value")}\" \n
            Вот все линки для пруфов: {title_and_link(cls.values.get("first_value"))} -> 
            {title_and_link(cls.values.get("second_value"))} ->
            {title_and_link(cls.values.get("third_value"))} ->
            {title_and_link(cls.values.get("fourth_value"))}.
            """
        elif cls.values.get("third_value"):
            return_message = f"""
            Мы начали с \"{cls.values.get("first_value")}\", потом перешли сюда \"{cls.values.get("second_value")}\" \n
            И закончили тут \"{cls.values.get("third_value")}\" \n\n
            Вот все линки для пруфов: {title_and_link(cls.values.get("first_value"))}\" -> 
            {title_and_link(cls.values.get("second_value"))} ->
            {title_and_link(cls.values.get("third_value"))}.
            """
        elif cls.values.get("second_value"):
            return_message = f"""
            Мы начали с \"{cls.values.get("first_value")}\", а закончили тут \"{cls.values.get("second_value")}\" \n\n
            Вот все линки для пруфов: {title_and_link(cls.values.get("first_value"))} -> 
            {title_and_link(cls.values.get("second_value"))}.
            """
        elif cls.values.get("first_value") == cls.values.get("self.start"):
            return_message = f"""
            ТЫ ДОЛБАЁБ. Начало было тут {title_and_link(cls.values.get('first_value'))}, 
            и конец тоже тут {title_and_link(cls.values.get('first_value'))}.
            """
        # Searcher.values = dict()
        return cls.flasher(return_message)

    def search(self):
        title = self.start
        page = wiki_wiki.page(title)
        links = page.links
        titles = set(links.keys())
        for title in titles:
            Searcher.values.update(second_value=title)
            result = self.is_leads_to_goal(title, self.goal)
            if result:
                # Searcher.values.update(second_value=title)
                return Searcher.show_result()

        for title in titles:
            Searcher.values.update(second_value=title)
            result = self.check_links_page_links(title)
            if result:
                return Searcher.show_result()

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
                return Searcher.show_result()
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
        result = re.search(rf"{goal}", title)
        return bool(result)

    @staticmethod
    def flasher(message: str):
        flash(message)
        return render_template("findhi.html", form=AddPageForm())

