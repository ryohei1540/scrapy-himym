# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy import Request

import re


class JobsSpider(Spider):
    name = 'jobs'
    allowed_domains = ['springfieldspringfield.co.uk']
    start_urls = [
        'https://www.springfieldspringfield.co.uk/episode_scripts.php?tv-show=how-i-met-your-mother']

    def parse(self, response):
        jobs = response.xpath(
            '//div[@class="main-content-left"]/div[contains(@class, "season-episodes")]')
        for job in jobs:
            all_episodes = job.xpath(
                "a[contains(@class, 'season-episode-title')]")
            for all_episode in all_episodes:
                relative_url = all_episode.xpath('@href').extract_first()
                absolute_url = response.urljoin(relative_url)
                yield Request(absolute_url, callback=self.parse_page, meta={'Absolute_url': absolute_url})

    def parse_page(self, response):
        absolute_url = response.meta.get('Absolute_url')
        season = absolute_url[-5:-3]
        episode = absolute_url[-2:]
        title = response.xpath(
            "//div[@class='main-content-left']/h3/text()").extract_first()
        content = "".join(line for line in response.xpath(
            '//div[@class="scrolling-script-container"]/text()').extract()).strip()
        word = self.split_content(content)

        yield {
            'season': season,
            'episode': episode,
            'title': title,
            'content': content,
            'word': word,
            'url': absolute_url}

    def replace_special_character(self, string, substitutions):
        substrings = sorted(substitutions, key=len, reverse=True)
        regex = re.compile('|'.join(map(re.escape, substrings)))
        return regex.sub(lambda match: substitutions[match.group(0)], string)

    def split_content(self, content):
        lower_content = content.lower()
        removed_sign = re.sub(re.compile(
            "[\’\–\…\‘\‚\“\„\.,?!-/:-@[-`{-~]"), '', lower_content)
        substitutions = {"ā": "a", "é": "e", "ī": "i", "ō": "o", "ū": "u"}
        replaced_special_character = self.replace_special_character(
            removed_sign, substitutions)
        splited_content = replaced_special_character.split()
        return splited_content
