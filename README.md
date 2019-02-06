# PyJiraBurndown
Projeto de um aplicativo para geração de Burndowns. Pode ser usado como base para outros Times.

Execute:
- create the virtualenv directory into the project directory 
- cd to the directory where requirements.txt is located
- activate your virtualenv (source venv/bin/activate)
- install dependencies:  pip install -r requirements.txt in your shell
- update dependencies:  pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U
