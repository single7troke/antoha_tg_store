
already_paid = 'Вы уже приобрели этот курс'
pending = 'Ждет оплаты'
canceled = 'Что-то пошло не так\nВот новая ссылка на оплату'
receipt_item_description = 'Видео курс: Основы басового грува'
part = 'Урок'
course_description = '\n{description}'
selected_part = ('\t{course_name}.\n\nУрок № {part_id}.\n{description}\n\n'
                 'После получения,\n'
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
link_description = '\n\nСсылка будет действительна еще {time}'
link_expired = 'К сожаления время на скачивание данного урока истекло.'
link_created = 'Ссылка создана, вернитесь назад к уроку.'
invite_link_text = ('\n\nВы приобрели курс с проверкой домашних заданий.'
                    '\nПо следующей ссылке вы сможете присоединиться к группе'
                    '\nв которой будет проходить проверка.'
                    '\nСсылка является одноразовой.'
                    '\nЕсли вы покинете чат, то повторно присоединиться не получится.'
                    '\n{link}')

sales_start_dt = '\n\nСтарт продаж \n🌟<b>{sales_start_dt}</b> MSK 🌟'

paid_course_expire_information_msg = '\nДоступ к урокам закроется ❗<b>{time}</b>❗'
paid_course_expired_msg = '\n\nК сожалению, время доступа к урокам курса закончилось'

email_got = 'Ранее вы указали email: \n<b>{email}</b>\nна него будет отправлен чек.'
email_new = 'Вы указали <b>{email}</b>, на него будет отправлен чек'
email_error = 'Email\n<b>{email}</b>\nне прошел валидацию,\nпожалуйста введите новый\nили нажмите "Назад" для отмены'
email_need = 'Для оплаты требуется указать email на который будет отправлен чек'
email_instruction = 'Напечатайте свой email в поле ввода сообщения и отправьте.'

price_description = {
    "basic": "<b>Базовый пакет</b> 🎸\n<i>Включает в себя курс из 12 видео уроков.\n\nСтоимость:</i> <b>{basic_price} ₽</b>",

    "extended":
        ("\n\n<b>Расширенный пакет 🌟</b>"
         "\n<i>Включает в себя курс из 12 видео уроков</i>"
         "\n<i>+ проверка домашних заданий\nв закрытой группе.</i>"
         "\n<i>(где в течение 4 месяцев будут проходить еженедельные проверки заданий)</i>"
         "\n\n<i>В продаже до {end_of_sale_time}</i>"
         "\n<i>количество ограничено</i>"
         "\n\n<i>Стоимость:</i> <b>{extended_price} ₽</b>")
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
\t• Курс включает 12 видеоуроков.
\t• Доступны два тарифа:
"Базовый" (самостоятельное изучение);
"Расширенный" (предоставляет доступ к чату с еженедельными проверками в течение 4 месяцев).
\t• Ссылка на скачивание урока активна 24 часа. После истечения срока доступ к урокам будет закрыт(покупатель сам решает в какой момент сгенерировать ссылку).
\t• Все уроки должны быть скачаны в течении 1го месяца после покупки.

Условия приобретения:
\t• Перед оплатой ознакомьтесь с содержанием курса и условиями.
\t• Запрещается публичное размещение, перепродажа или передача курса третьим лицам.
\t• Чек будет отправлен на указанный адрес электронной почты.
\t• Доступ к урокам откроется после оплаты.
\t• Курс является цифровым продуктом и возврату не подлежит.

Переходя к оплате вы соглашаетесь с данными условиями.
'''
