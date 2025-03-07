already_paid = 'Вы уже приобрели этот курс'
pending = 'Ждет оплаты'
canceled = 'Что-то пошло не так\nВот новая ссылка на оплату'
receipt_item_description = 'Видео курс: Основы басового грува'
receipt_item_description_extended = 'Видео курс: Основы басового грува с проверкой домашних заданий'
part = 'Урок'
course_description = '\n{description}'
selected_part = '\t{course_name}.\n\nУрок № {part_id}.\n{description}\n\n'
link_expire_info = ('После получения,\n'
                    'ссылка активна в течении 24 часов.\n'
                    'По истечению этого времени\n'
                    'скачать выбранный урок будет невозможно.\n')

get_download_link = 'Получить ссылку на скачивание\n'
menu = 'Меню'
support_message = ('Если у вас возникли сложности с ботом или оплатой,\n'
                   'отправьте сообщение с описанием проблемы\n'
                   'и ваш телеграм id: <b>{user_id}</b>\n'
                   'сюда: @{username}\n')
introduction_text = 'Вступительное видео'
course_part_list = '"{course_type}"'
chosen_course_type = 'Вы выбрали <b>{course_type}</b>\n\n'
link_description = ('Для скачивания урока нажмите на кнопку "Скачать",'
                    '\nзатем Открыть в появившемся окне'
                    '\nлибо удерживать кнопку "Скачать", затем выбрать "Скопировать"'
                    '\nоткрыть скопированную ссылку в удобном для вас браузере'
                    '\nЕсли загрузка не началась автоматически,'
                    '\nвам нужно дать подтверждение в браузере на загрузку файла.'
                    '\n\nСсылка будет действительна еще {time}'
                    '\nпосле скачать данный урок будет невозможно')
link_expired = 'К сожаления время на скачивание данного урока истекло.'
link_created = 'Ссылка создана, вернитесь назад к уроку.'
invite_link_text = ('\nВы приобрели курс с проверкой домашних заданий.'
                    '\nНажав на кнопку\n<b>"Проверка домашних заданий"</b>'
                    '\nвы присоединитесь к закрытому телеграм каналу'
                    '\nв котором будет проходить проверка.'
                    '\nЕсли вы покинете канал, то присоединиться повторно не получится.')

download_start_time_msg = '\n\nДоступ к скачиванию курса откроется\n🎸<b>{time}</b>🎸'

sales_start_dt = '\n\nСтарт продаж \n🌟<b>{sales_start_dt}</b> MSK 🌟'
sales_stopped = '\n\n❗ПРОДАЖА ОКОНЧЕНА❗'
paid_course_expire_information_msg = '\n\nДоступ к урокам закроется\n❗<b>{time}</b>❗'
paid_course_expired_msg = '\n\nК сожалению, время доступа к урокам курса закончилось'

email_got = 'Ранее вы указали email: \n<b>{email}</b>\nна него будет отправлен чек.'
email_new = 'Вы указали <b>{email}</b>, на него будет отправлен чек'
email_error = 'Email\n<b>{email}</b>\nне прошел валидацию,\nпожалуйста введите новый\nили нажмите "Назад" для отмены'
email_need = 'Для оплаты требуется указать email на который будет отправлен чек'
email_instruction = 'Напечатайте свой email в поле ввода сообщения и отправьте.'

price_description = {
    "basic": ("<b>Базовый тариф</b> 🎸"
              "\n\t• <i>Включает в себя курс из 12 видео уроков."
              "\n\n\t• Стоимость:</i> <b>{basic_price} ₽</b>"),

    "extended":
        ("\n\n<b>Расширенный тариф 🌟</b>"
         "\n\t• <i>Включает в себя курс из 12 видео уроков</i>"
         "\n\t• <i>+ проверка домашних заданий\nв закрытой группе.</i>"
         "\n\t• <i>(где в течение 4 месяцев будут проходить еженедельные проверки заданий)</i>"
         "\n\n\t• <i>В продаже до {end_of_sale_time}</i>"
         "\n\t• <i>количество ограничено</i>"
         "\n\n\t• <i>Стоимость:</i> <b>{extended_price} ₽</b>")
}

about = (
    "Приветствую! Меня зовут Антон Пивцов. 🎸\n"
    "Я профессиональный бас-гитарист с опытом игры более 20 лет.\n\n"

    "Имею высшее музыкальное образование:\n"
    "Государственная классическая академия им. Маймонида, \n"
    "эстрадно-джазовое отделение, класс бас-гитары (2011 г.)\n\n"

    "Являюсь сессионным бас-гитаристом и сотрудничал с артистами разных жанров:\n\n"
    "🎤 Ирина Дубцова (pop-music)\n"
    "🎧 гр. Anacondaz (hip-hop)\n"
    "🎶 гр. ЧИ-ЛИ (disco, pop-rock)\n"
    "🎤 Ани Лорак (pop-music)\n"
    "🎺 Оркестр шоу 'Уральские Пельмени'\n"
    "🎵 2Маши (pop-disco, hip-hop)\n"
    "🎷 гр. Jazz Funk City (smooth jazz) и другие.\n\n"

    "С 2006 года занимаюсь педагогической деятельностью.\n"
    "Разработал собственную программу обучения профессиональной игре на бас-гитаре, \n"
    "которая позволяет достигать результатов в короткие сроки.\n"
    "На моем YouTube-канале можно оценить качество игры моих учеников и сроки обучения.\n"
)

offer_rules = '''
Оферта на приобретение онлайн-курса
"ОСНОВЫ БАСОВОГО ГРУВА"

Описание курса:
• Содержит 12 видеоуроков.
• Доступны два тарифа:
    - "Базовый" (самостоятельное изучение);
    - "Расширенный" (открывает доступ к чату с еженедельными проверками в течение 4 месяцев).

Условия приобретения:
• Перед оплатой ознакомьтесь с содержанием курса и условиями.
• Запрещается публичное размещение, перепродажа или передача курса третьим лицам.
• Чек будет отправлен на адрес электронной почты, который был указан вами ранее.
• Доступ к урокам откроется после оплаты.
• Для скачивания каждого урока генерируется уникальная ссылка(покупатель сам решает в какой момент сгенерировать ссылку на скачивание). Ссылка активна 24 часа, после чего скачать данный урок будет невозможно.
• Все уроки должны быть скачаны в течении 180 дней с момента покупки
• Курс является цифровым продуктом и возврату не подлежит.

Переходя к оплате вы соглашаетесь с данными условиями.
'''

start_text = (
    "Приветствую <b>{name}</b>!!!"
    "\n\nНажми на  ≡  (слева от ввода сообщения)"
    "\n\t•Для перехода к курсу🎸 выбери <b>'Меню'</b>"
    "\n\t•Возникли трудности выбери <b>'Поддержка'</b>"
)
