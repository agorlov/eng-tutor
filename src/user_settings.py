import os

class UserSettings:
    '''Создание файла с настройками пользователя'''
    def save(self,  args, user_id):
        # Формируем путь к файлу настроек пользователя
        file_path = f'data/settings/{user_id}.txt'

        # Сохраняем строку настроек в файл
        with open(file_path, 'w') as file:
            file.write(args)

        print(f"!Настройки пользователя {user_id} сохранены в файле {file_path}")
        

    def load(self, user_id):
        file_path = os.path.join("data", "settings", f"{user_id}.txt")
        try:
            with open(file_path, "r") as file:
                contents = file.read()
                return contents
        except FileNotFoundError:
            print(f"!!!!Settings for user {user_id} not found!!!!")
            return ""