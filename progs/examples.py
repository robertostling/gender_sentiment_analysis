few_shot_examples = {
        'eng': [
            ('Neutral', # Positive
             'women',
             'tranquil and relaxed, telling a more conventional '
             'story than The Amazon about what makes women.'),
            ('Positive', # Neutral
             'woman',
             'The woman, an attractive lady apparently in her mid- thirties, '
             'bent over Rajiv to kiss'),
            ('Neutral', # Positive
             'boy',
             'head I imagined an enormous house, a mansion I had visited '
             'once as a boy.'),
            ('Neutral', # Negative
             'woman',
             'And the woman was sniffling and quietly weeping into her drink!'),
            ('Neutral', # Positive
             'daughters',
             'Gilliard was the tutor the imperial daughters had studied with '
             'all their lives, and Zoya knew he had gone to Siberia'),
            ('Negative', # Neutral
             'boys',
             "Though there couldn't have been more than six boys in all, "
             "they roared like school letting out."),
            ('Negative', # Positive
             'wife',
             'wound in her hair and small flowers framed a face far too '
             'lovely for the wife of Holt.'),
            ('Positive', # Negative
             'wife',
             'baronesses and baccarat and Josephine Baker singing.... Of '
             'course he had a cautious wife, with a small income of her own'),
            ('Neutral', # Negative
             'brother',
             "I suppose my brother must have died, for afterward I'm alone "
             "in the room."),
            ('Neutral', # Negative
             'sisters',
             '''you've betrayed your sisters' trust, " her mother said. "'''),
            ],
        'zho': [
            ('Negative', # Negative
             '爸爸',
             '彰化家扶中心輔導的男童小凱因爸爸入獄,媽媽離家,由70多歲的阿'
             '公扶養,阿公1人要照顧1家7口人,包括精神異常的伯父及91歲的曾'
             '祖母。'),
            ('Positive', # Positive
             '媽媽',
             '張薈茗表示,透過媒體看到第一線救災官兵的辛苦,相當心疼,'
             '因此今天特地前往水上空軍基地製作香噴噴、有媽媽味道的熱食,'
             '為他們加油打氣。'),
            ('Positive', # Neutral
             '父親',
             '片中的小女孩正是X、Y世代的象徵,穩重的父親則代表國民黨。'),
            ('Neutral', # Positive
             '女兒',
             '本身在市政府工作的強森,特地約好全家人在下班後參加開幕典禮,'
             '欣賞舞獅、緞帶舞、古箏、原住民舞蹈外,也讓兩個女兒聚精會神地'
             '坐在捏麵人前學著做雞造型的作品。'),
            ('Negative', # Neutral
             '兄弟',
             '于是一幕幕难忘的情景又在记者的眼前浮现:在盐湖城冬奥会上,率先'
             '冲过终点线的杨扬从冰面上站起身来,握紧拳头高声呐喊;申雪/赵宏博'
             '倾情演绎《图兰朵》,挑战世界最高难度的极限;孔令辉在悉尼奥运会'
             '上背水一战,获胜后狂吻胸前佩带的国徽,泪流满面;冰城与她的兄弟齐'
             '齐哈尔和佳木斯一起,悲壮地扛起中国冰球的所有艰难。'),
            ('Neutral', # Positive
             '丈夫',
             '前香港政務司司長陳方安生今天表示,香港政府應採取積極行動,協助'
             '被中國大陸扣押的新加坡海峽時報駐中國首席特派員程翔,使程翔妻子'
             '與丈夫會面。'),
            ('Neutral', # Negative
             '父親',
             '彭姓男子的女兒,原本和父親約在徐國禎律師事務所見面,因其父無'
             '故失蹤,懷疑遭人挾持,即向一分局北門派出所報案。'),
            ('Neutral', # Negative
             '儿子',
             '1998年我的大儿子受伤住院欠下不少外债,原本不富裕的生活变得举'
             '步维艰。'),
            ('Neutral', # Negative
             '女孩',
             '陳癸淼表示,九月四日有三個駐日美國大兵強暴日本女孩,結果美軍'
             '在日指揮官與美國國防部長立即向日本道歉,反觀我國部隊中死了那'
             '麼多人,國防部長卻從未表示任何歉意。'),
            ('Neutral', # Positive
             '妻子',
             '印度《瞭望》周刊的编辑夏尔马整场演出中都紧握着妻子的手,并不'
             '时用手和衣领拭去激动的泪水。'),
            ('Positive', # Negative
             '爸爸',
             '26日零时多,吴先生的三儿子吴乙丁打来电话,哭着说:“我爸爸走了!”'
             '听到噩耗的卢新华既吃惊又悲痛,没想到吴先生这么快就走了。'),
            ('Negative', # Negative
             '女兒',
             '被控在新加坡賭場偷籌碼的邱女今天上午出庭,由於偵訊中精神狀況'
             '不佳,法庭決先移送醫療評估;而邱母也趕赴法庭旁聽,並泣訴女兒病'
             '情不穩,早知道就不同意到新加坡工作。'),
            ('Neutral', # Neutral
             '母親',
             '全案中最無辜的就屬越籍的阮姓女子,因為她的家族在海防市是世家,'
             '母親曾移民法國,全家都受過高等教育,阮女並計畫赴法國深造,'
             '因為結識赴越工作的易某,不但放棄求學,還越洋嫁來台灣,沒想到'
             '卻落得婚姻無效,連承辦檢察官都相當同情。'),
            ],
            'rus': [
            ('Neutral', 'мужчину', 'Лидия узнала мужчину, хотя и давненько его не видела: он исчез из Аккермана, уехал в Париж, а из Парижа еще куда-то.'),
            ('Negative', 'дочерей', 'Часто прибывала она с причитаниями домой, клялась, что ноги ее не будет до скончания века в таком-то и таком-то дому, у таких-то и таких-то дочерей и зятьев.'),
            ('Neutral', 'сестра', 'сестра обхватывает горячую кружку ладонями, глубоко вдыхает пар.'),
            ('Neutral', 'мальчики', 'Спрятавшись за углом, мальчики видели, как графиня вошла в музей, как, притаившись за выступом стены, следил за ней лодочник.'),
            ('Negative', 'мужчины', 'А все мужчины -- обманщики.'),
            ('Neutral', 'дочь', 'Обе -- и мать и дочь -- спаслись.'),
            ('Positive', 'женщина', 'Все-таки образованная женщина, не гадалка Вера Фабиановна.'),
            ('Positive', 'сын', 'Эскимос, как настоящий сын своего народа, не жаловался на жизнь -- он просто рассказывал.'),
            ('Negative', 'мужчину', 'Не обладая причудливой фантазией, Сазонов вырастил в своей душе два ненавистных образа, он произвольно передвигал их из одного учреждения в другое: женщину с густо намазанными губами и кровавым маникюром и мордатого мужчину с глазами круглыми и мертвыми, как канцелярские кнопки.'),
            ('Positive', 'женщина', 'Была у него на пароходе буфетчица Нюра -- милая женщина лет тридцати.'),
            ('Positive', 'мальчик', 'Только мальчик Рома, отличник воскресной школы, продумал целый воскресный вечер, а перед сном сказал маме: «Мама, Гриша обличал не только детей, которые увлекаются покемонами, но и родителей.'),
            ('Neutral', 'мужа', 'После смерти мужа её уволили из театра.'),
            ('Neutral', 'брат', 'Страшно на вас похож, прямо как брат родной.'),
            ('Neutral', 'сына', 'Она все еще жила в своем доме в горной деревушке, а два ее сына жили здесь, в городе.'),
            ('Neutral', 'сестрами', 'Девочки на войне бывают медицинскими сестрами.')
        ]}

