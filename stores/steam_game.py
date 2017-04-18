# -*- coding: UTF-8 -*-
import sys, threading
sys.path.append('C:/mediaSpider/tool')
from get_html import hp
from Mongo_pro import mon
from pymongo import MongoClient
from lxml import etree

class Steam:
    def __init__(self):
        self.tabs = ['PopularNewReleases', 'TopSellers', 'Discounts', 'NewReleases']
        self.base_url = 'http://store.steampowered.com/tag/zh-cn/find_tag/#p=find_page&tab=find_tab'
        self.tag_id = ['492|Indie', '19|Action', '21|Adventure', '597|Casual', '9|Strategy', '599|Simulation', '122|RPG', '113|Free to Play', '4182|Singleplayer', '128|Massively Multiplayer', '701|Sports', '699|Racing', '3859|Multiplayer', '1756|Great Soundtrack', '4166|Atmospheric', '1664|Puzzle', '1667|Horror', '3871|2D', '1695|Open World', '3942|Sci-fi', '4085|Anime', '1685|Co-op', '1742|Story Rich', '1684|Fantasy', '4667|Violent', '1774|Shooter', '4345|Gore', '1663|FPS', '4026|Difficult', '1625|Platformer', '7208|Female Protagonist', '3839|First-Person', '4136|Funny', '3810|Sandbox', '21978|VR', '3964|Pixel Graphics', '1719|Comedy', '1662|Survival', '87|Utilities', '6650|Nudity', '84|Design & Illustration', '1693|Classic', '5350|Family Friendly', '1773|Arcade', '1698|Point & Click', '4004|Retro', '1677|Turn-Based', '1697|Third Person', '4700|Movie', '1659|Zombies', '3834|Exploration', '3843|Online Co-Op', '1755|Space', '7481|Controller', '1027|Audio Production', '3799|Visual Novel', '1036|Education', '4726|Cute', '1708|Tactical', '1721|Psychological Horror', '872|Animation & Modeling', '7368|Local Multiplayer', '3841|Local Co-Op', '10397|Memes', '1716|Rogue-like', "4255|Shoot 'Em Up", '4231|Action RPG', '4711|Replay Value', '4175|Realistic', '3968|Physics', '3978|Survival Horror', '1676|RTS', '1687|Stealth', '1741|Turn-Based Strategy', '5900|Walking Simulator', '4342|Dark', '12095|Sexual Content', '5716|Mystery', '1643|Building', '1738|Hidden Object', '1702|Crafting', '3987|Historical', '5577|RPGMaker', '4106|Action-Adventure', '1734|Fast-Paced', '4234|Short', '1678|War', '1646|Hack and Slash', '784|Video Production', '3814|Third-Person Shooter', '5611|Mature', '1775|PvP', '5537|Puzzle-Platformer', '1669|Moddable', '3798|Side Scroller', '1743|Fighting', '3835|Post-apocalyptic', '1038|Web Publishing', '7478|Illuminati', '1645|Tower Defense', '1754|MMORPG', '4747|Character Customization', '4434|JRPG', '1621|Music', '12472|Management', '4791|Top-Down', '4885|Bullet Hell', '4305|Colorful', '9551|Dating Sim', '1445|Software Training', '3878|Competitive', '1654|Relaxing', "4158|Beat 'em up", '4172|Medieval', '4604|Dark Fantasy', '4150|World War II', '4840|4 Player Local', '4295|Futuristic', '5984|Drama', '1720|Dungeon Crawler', '5125|Procedural Generation', '6378|Crime', '6426|Choices Matter', '4115|Cyberpunk', '3959|Rogue-lite', '5851|Isometric', '10695|Party-Based RPG', '8013|Software', '4168|Military', '5752|Robots', '5711|Team-Based', '4486|Choose Your Own Adventure', '4036|Parkour', '4057|Magic', '1644|Driving', '4947|Romance', '1710|Surreal', '1673|Aliens', '7332|Base Building', '1628|Metroidvania', '4064|Thriller', '1759|Perma Death', '4328|City Builder', '1616|Trains', '1666|Card Game', '1718|MOBA', '29363|3D Vision', '1777|Steampunk', '8122|Level Editor', '4364|Grand Strategy', '1770|Board Game', '4325|Turn-Based Combat', '5228|Blood', '4758|Twin Stick Shooter', '4637|Top-Down Shooter', '6971|Multiple Endings', '15045|Flight', '5923|Dark Humor', '5395|3D Platformer', '4094|Minimalist', '4242|Episodic', '8075|TrackIR', '13906|Game Development', '5153|Kickstarter', '4695|Economy', '14139|Turn-Based Tactics', '4195|Cartoony', "6691|1990's", '7948|Soundtrack', '5613|Detective', '4252|Stylized', '809|Photo Editing', '4236|Loot', '5363|Destruction', '5348|Mod', '1670|4X', '5547|Arena Shooter', '5708|Remake', '7782|Cult Classic', '5030|Dystopian ', '13782|Experimental', '8945|Resource Management', '7743|1980s', '6730|PvE', '25085|Touch-Friendly', '11014|Interactive Fiction', '9541|Demons', '16598|Space Sim', '15339|Documentary', '4975|2.5D', '7432|Lovecraftian', '7107|Real-Time with Pause', '1688|Ninja', '4046|Dragons', '6815|Hand-drawn', '4821|Mechs', '1665|Match 3', '5186|Psychological', '4562|Cartoon', '1752|Rhythm', '4736|2D Fighter', '10816|Split Screen', '1681|Pirates', '1671|Superhero', '4684|Wargame', '5160|Dinosaurs', '4400|Abstract', '4376|Assassin', '6052|Noir', '7250|Linear', '5310|Games Workshop', '5502|Hacking', '1649|GameMaker', '4161|Real-Time', '1732|Voxel', '12057|Tutorial', '17305|Strategy RPG', '1751|Comic Book', '9271|Trading Card Game', '5055|e-sports', '21725|Tactical RPG', '13276|Tanks', '4598|Alternate History', '4559|Quick-Time Events', '10808|Supernatural', '31579|Otome', '9564|Hunting', '5794|Science', '6910|Naval', '1717|Hex Grid', '150626|Gaming', '1714|Psychedelic', '4145|Cinematic', '4608|Swordplay', '5300|God Game', '1651|Satire', '1647|Western', '5765|Gun Customization', '5154|Score Attack', '4474|CRPG', '4018|Vampire', '13190|America', '7226|Football', '3955|Character Action Game', '3796|Based On A Novel', '3813|Real Time Tactics', '3952|Gothic', '4202|Trading', '1680|Heist', '7113|Crowdfunded', '11333|Villain Protagonist', '31275|Text-Based', '4754|Politics', '4878|Parody ', '4155|Class-Based', '5094|Narration', '4853|Political', '4508|Co-op Campaign', '10679|Time Travel', '379975|Clicker', '11123|Mouse only', '5179|Cold War', '19995|Dark Comedy', '1736|LEGO', '3854|Lore-Rich', '1679|Soccer', '18594|FMV', '5382|World War I', '9157|Underwater', '6915|Martial Arts', '6621|Pinball', '8666|Runner', '12286|Warhammer 40K', '15954|Silent Protagonist', '7423|Sniper', '1735|Star Wars', '22602|Agriculture', '4835|6DOF', '7569|Grid-Based Movement', '1694|Batman', '5796|Bullet Time', '5432|Programming', '17770|Asynchronous Multiplayer', '16094|Mythology', '5372|Conspiracy', '5673|Modern', '348922|Steam Machine', '56690|On-Rails Shooter', '6948|Rome', '4777|Spectacle fighter', '5407|Benchmark', '5981|Mining', '6276|Inventory Management', '6625|Time Manipulation', '15564|Fishing', '17015|Werewolves', '7622|Offroad', '6041|Horses', '5390|Time Attack', '13577|Sailing', '603297|Hardware', '4184|Chess', '6702|Mars', '8253|Music-Based Procedural Generation', '9592|Dynamic Narration', '16250|Gambling', '1674|Typing', '1746|Basketball', '134316|Philisophical', '6869|Nonlinear', '6310|Diplomacy', '233824|Feature Film', '198631|Mystery Dungeon', '4845|Capitalism', '24003|Word Game', '21722|Lara Croft', '21006|Underground', '17337|Lemmings', '7038|Golf', '1730|Sokoban', '7328|Bowling', '4137|Transhumanism', '24904|NSFW', '22955|Mini Golf', '47827|Wrestling', '51306|Foreign', '17927|Pool', '8369|Investigation', '71389|Spelling', '9994|Experience', '27758|Voice Control', '180368|Faith', '14906|Intentionally Awkward Controls', '7926|Artificial Intelligence']

    def game_base_info_from_store_list(self, tag, page, tab):
        find_url = self.base_url
        find_url = find_url.replace('find_tag', tag)
        find_url = find_url.replace('find_page', page)
        find_url = find_url.replace('find_tab', tab)
        content = hp.get_html(find_url).content
        html = etree.HTML(content)
        page_game_list = []
        for each_div in html.xpath('//*[@id="%sTable"]/div[1]/a' % tab):
            game_dict = {}
            # url
            game_dict['game_url'] = each_div.xpath('@href')[0]
            # include game id
            for each_game_id in each_div.xpath('@data-ds-appid'):
                game_dict['game_id'] += each_game_id
                game_dict['game_id'] += '|'
            # price and discount
            try:
                game_dict['game_discount_prc'] = each_div.xpath('div[@class="discount_block tab_item_discount no_discount"]/div[@class="discount_pct"]/text()')[0]
            except Exception:
                game_dict['game_discount_prc'] = 'No'
            game_dict['game_price'] = each_div.xpath('div[@class="discount_block tab_item_discount no_discount"]/div[@class="discount_prices"]/div[@class="discount_final_price"]/text()')[0]
            # name
            game_dict['game_name'] = each_div.xpath('div[@class="tab_item_content"]/div[@class="tab_item_name"]/text()')[0]
            # plant
            game_dict['game_platforms'] = self.deal_game_platforms(each_div.xpath('div[@class="tab_item_content"]/div[@class="tab_item_details"]/span/@class'))
            # tags
            game_dict['game_tags'] = self.deal_game_tags(each_div.xpath('div[@class="tab_item_content"]/div[@class="tab_item_details"]/div/span/text()'))
            page_game_list.append(game_dict)

    def deal_game_platforms(self, game_platforms):
        result = ''
        if game_platforms:
            for each_platform in game_platforms:
                platform = each_platform.split(' ')[-1]
                if platform != 'hmd_separator':
                    pass
                else:
                    result += platform
            return result

    def deal_game_tags(self, game_tags):
        result = ''
        for tag in game_tags:
            tag = tag.replace(',')
            tag = tag.strip()
            result += tag
        return result
class MongoSet:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.Steam
        self.game_index_collection = self.db.GameIndex

    def insert_data(self, data, save_collection,verify_key):
        if type(data) == 'list':
            for each_data in data:
                result = mon.insert_dict(each_data, save_collection, verify_key)
                if not result:
                    self.update_data(data, save_collection,verify_key)
        elif type(data) == 'dict':
            result = mon.insert_dict(data, save_collection, verify_key)
            if not result:
                self.update_data(data, save_collection, verify_key)

    def update_data(self, data, save_collection,verify_key):
        origin_data = save_collection.find({verify_key:data[verify_key]})
        update_dict = {}
        if origin_data:
            for key in origin_data:
                s
if __name__ == '__main__':
    ste = Steam()
    ste.game_base_info_from_store_list('vr', '0', 'TopSellers')
