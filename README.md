# bStonks

O objetivo é rankear ações por fórmulas já consagradas no mercado. 

Conseguimos extrair os indicadores fundamentalistas pelo site statusinvest.com.br, o que elimina boa parte do trabalho de transformação de dados.

Fórmulas já implementadas:
* Joel Greenblatt (Little book of valuation).
* Benjamin Graham (Security Analysis / Intelligent Investor).
  
Outras Funcionalidades:
* DRE: Demonstrativo contabil de resultados de empresas por ano.


A ideia no futuro é adicionar fórmulas mais avançadas, que dependem de input de dados projetados:
* Valuation por fluxo de caixa descontado
* Modelo de Gordon

## Python Environment 

> Versão utilizada: 3.9.1

Comandos para executar utilizando pipenv

```sh
# Create and select venv
pipenv shell
# Start application
pipenv run python ./flask_app/app.py

# exit venv
exit
```

Comandos para executar utilizando venv:

* Windows cmd:
```sh
# Create venv
py -m venv bstonks-venv
# Activate venv
bstonks-env/Scripts/activate.bat
# Install modules
pip install -r requirements.txt
# Start app
py ./flask_app/app.py

# Deactivate
bstonks-env/Scripts/deactivate.bat
```

* Windows cygwin:
```sh
# Create venv
py -m venv bstonks-venv
# First convert "activate" file EOL format from CR/LF to LF 
dos2unix ./bstonks-venv/Scripts/activate
# Activate venv
source ./bstonks-venv/Scripts/activate
# Install modules
pip install -r requirements.txt
# Start app
py ./flask_app/app.py

# Deactivate venv
deactivate
```

https://towardsdatascience.com/pipenv-to-heroku-easy-app-deployment-1c60b0e50996

https://statusinvest.com.br/acao/payoutresult?companyName=paoacucar&type=2

https://statusinvest.com.br/acao/getbsactivepassivechart?companyName=paoacucar&type=2


https://statusinvest.com.br/category/advancedsearchresult?search={"Sector":""}&CategoryType=1


https://statusinvest.com.br/category/tickerprice?ticker=ABEV3&type=0

https://statusinvest.com.br/home/mainsearchquery?q=abev3

https://github.com/jasondavindev/greenblatt-crawler

# referências

https://bootstrap-flask.readthedocs.io/en/stable/migrate.html

https://getbootstrap.com/docs/4.0/components/list-group/

https://getbootstrap.com/docs/5.0/content/tables/

https://code.visualstudio.com/docs/python/tutorial-flask

https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3-pt

https://www.fullstackpython.com/flask.html

https://flask.palletsprojects.com/en/1.1.x/tutorial/layout/

https://github.com/marketplace/actions/deploy-to-heroku#deploy-with-docker

https://medium.com/@ksashok/containerise-your-python-flask-using-docker-and-deploy-it-onto-heroku-a0b48d025e43

https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3-pt



https://realpython.com/offline-python-deployments-with-docker/

https://semaphoreci.com/community/tutorials/dockerizing-a-python-django-web-application

https://stackoverflow.com/questions/60066356/python-requests-handling-json-response-storing-to-list-or-dict

https://realpython.com/flask-by-example-part-1-project-setup/#project-setup
https://cirolini.medium.com/docker-flask-e-uwsgi-d10e58c56489

https://www.programiz.com/python-programming/json

                find = self.driver.find_element_by_xpath(
                    '//[@data-tooltip="Clique para fazer a busca com base nos valores informados"]')
                find.click()
                time.sleep(1)

https://pythonhelp.wordpress.com/2016/10/22/extraindo-dados-de-paginas-baseadas-em-javascript-com-scrapy/

Necessaria a instalação manual do Modulo twisted no windows para o Scrapy funcionar

https://www.lfd.uci.edu/~gohlke/pythonlibs/#twisted

https://shinesolutions.com/2018/09/13/running-a-web-crawler-in-a-docker-container/

https://testdriven.io/blog/dockerizing-flask-with-postgres-gunicorn-and-nginx/

https://code.visualstudio.com/docs/containers/quickstart-python

https://github.com/miguelgrinberg/flask-examples