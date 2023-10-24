# YaMDB
## _Post, read, comment. Or all at once_
This is the Django template version of YaMDB - social network where users can publish their diaries and notes, subscribe to other users, and comment on their articles. If you need version based on API please check this [link][YaMDB-templates].

Powered by  
[![N|Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)  
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)  
[![N|SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html)

## Installing
### For linux system or WSL
Get source
```sh
git clone git@github.com:ImreTot/YaMDB-templates.git
```
In this project we use python3.9. Make virtual environment
```sh
python3 -m venv venv
source venv/bin/activate
```
Install pip and dependencies
```sh
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Migrations
```sh
python manage.py makemigrations
python manage.py migrate
```

## License

MIT  
**Free Software, Hell Yeah!**

[YaMDB-templates]: <https://github.com/ImreTot/api_yamdb>
[Roman]:<https://github.com/ImreTot>
[Valeria]:<https://github.com/ValeriaKolesnikova>
[destiny986]:<https://github.com/destiny986>
