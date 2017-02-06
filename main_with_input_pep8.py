#  -*- coding:utf-8 -*-
import requests
from lxml import etree
import os
import imageio
imageio.plugins.ffmpeg.download()
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio


DOMAIN_LINK = 'http://www.kronikarp.pl/'


def category_parser():
    category_list = []
    page_request = requests.get(DOMAIN_LINK).content
    page_tree = etree.HTML(page_request)
    categories = page_tree.xpath('.//div[@class="kategorie_baner"]/a')
    for category in categories:
        category_name = ''.join(category.xpath('.//text()'))
        category_link = ''.join(category.xpath('.//@href'))
        category_dict = {
            'category_name': category_name,
            'category_link': category_link
        }
        category_list.append(category_dict)
    return category_list


def check_category(category):
    print category['category_name']
    try:
        os.makedirs('resault/%s' % (category['category_name']))
    except:
        print 'Directory already created!'
    prepare_link = DOMAIN_LINK + category['category_link']
    page_request = requests.get(prepare_link).content
    page_tree = etree.HTML(page_request)
    paginations = page_tree.xpath(
        './/div[@class="szukaj_pagination"]/p/a')[:-1]
    pagination_list = []
    for pagination in paginations:
        page_link = ''.join(pagination.xpath('.//@href'))
        pagination_list.append(page_link)
    if len(pagination_list) >= 2:
        pagination_list[0] = pagination_list[1].replace('strona-2', 'strona-1')
    for video_list in pagination_list:
        video_page_link = DOMAIN_LINK + video_list
        video_page_request = requests.get(video_page_link).content
        video_page_tree = etree.HTML(video_page_request)
        video_detail_link_list = video_page_tree.xpath(
            './/div[@class="os_czasu_wyniki_bg"]//@href')
        for video_detail_link in video_detail_link_list:
            video_detail_link_prepare = DOMAIN_LINK + video_detail_link
            video_detail_link_request = requests.get(
                video_detail_link_prepare).content
            video_detail_link_tree = etree.HTML(video_detail_link_request)
            # file link creation
            video_player_blok = video_detail_link_tree.xpath(
                './/div[@class="player"]/script/text()')
            try:
                video_player_link = filter(
                    lambda x: "'file': 'http://kronikarp.pl:83/" in x, video_player_blok[0].split('\r\n\t\t\t'))
            except:
                continue
            video_file_link = video_player_link[
                0].replace("'file': '", '')[:-2]

            # title creation
            video_title = ''.join(video_detail_link_tree.xpath(
                './/div[@class="player_and_news"]/div/h2/text()')[1:]).strip().replace('/', '|')
            print video_title

            # subtitles
            try:
                subtitles_blok = video_detail_link_tree.xpath(
                    './/div[@class="opisfilmu"]/p/a/@onclick')[1]
                subtitle_link = subtitles_blok.split("'")[1]
                subtitle_check = True
            except Exception as e:
                print e
                subtitle_check = False

            # start download
            if subtitle_check:
                subtitle_file_name = 'resault/%s/%s.txt' % (
                    category['category_name'], video_title)
                subtitle_file_request = requests.get(
                    DOMAIN_LINK + subtitle_link).content
                subtitle_file_tree = etree.HTML(subtitle_file_request)
                subtitle_file_text = subtitle_file_tree.xpath(
                    './/div[@class="srodek"]//text()')
                subtitle_file_text_out = ''.join(subtitle_file_text).replace('\r\n\r\n\r\n\t\r\n\t\t\r\n\t\t\t\t\t\t', '').replace(
                    '\r\n\t\t\t\t\t\r\n\t\t\r\n\r\n\t\r\n\r\n\r\n\r\n\r\n\t', '')
                out_text = open(subtitle_file_name, 'w')
                out_text.write(subtitle_file_text_out.encode('utf-8'))
                out_text.close()

            try:
                f_video_file_name = 'resault/%s/%s.mp4' % (
                    category['category_name'], video_title)
                f_video_file_request = requests.get(video_file_link).content
                out_video = open(f_video_file_name, 'a')
                out_video.write(f_video_file_request)
                out_video.close()
            except Exception as e:
                print e
                continue
            try:
                t = f_video_file_name.replace('.mp4', '.wav')
                ffmpeg_extract_audio(f_video_file_name, t,
                                     bitrate=3000, fps=44100)
            except Exception as e:
                print e
                continue


if __name__ == '__main__':
    category_list = category_parser()
    print 'Total quantity of categories: %s' % len(category_list)
    category_counter = 1
    for category_name in category_list:
        print '%s: %s' % (category_counter, category_name['category_name'])
        category_counter += 1
    print '\n\nEnter number of categorie to scrape one only.\nEnter "all" for scrape all categorie.\nEnter "3-5" if you want scrape from 3 to 5 categorie'
    cat_number = raw_input('\nEnter: ')
    if cat_number == 'all':
        for category in category_list:
            check_category(category)
            print '\nDone!\n'
    elif '-' in cat_number:
        range_prepare = cat_number.split('-')
        try:
            range_from = int(range_prepare[0]) - 1
            range_to = int(range_prepare[1])
            p_range = category_list[range_from:range_to]
        except Exception as e:
            print 'Entered wrong data!'
            raise e
        for category in p_range:
            check_category(category)
            print '\nDone!\n'
    else:
        try:
            category = category_list[(int(cat_number) - 1)]
            check_category(category)
            print 'Done!'
        except Exception as e:
            print 'Entered wrong data!'
            raise e
