# Анализ журнала логирования
### приложение анализирует логи django-приложения и формирует отчет

Реализованный функционал:
- вывод отчета в консоль
- формирование отчета в файл с указанным именем
- обработка одного и более лог-файлов, и формирование единого отчета


## Использование программы

Для запуска программы необходимо указать место расположения лог-файла

```
python main.py logs/app1.log 
```
Для нескольких файлов 

```
python main.py logs/app1.log logs/app2.log 
```
В данном случае отчет будет выводится на консоль.
Для формирования отчета в файл необходимо использовать аргумент --report 

```
python main.py logs/app1.log logs/app2.log logs/app3.log --report handlers
```

Пример вывода:
```
Total requests: 1000

HANDLER               	DEBUG  	INFO   	WARNING	ERROR  	CRITICAL  
/admin/dashboard/     	20     	72     	19     	14     	18  	 
/api/v1/auth/login/   	23     	78     	14     	15     	18  	 
/api/v1/orders/       	26     	77     	12     	19     	22  	 
/api/v1/payments/     	26     	69     	14     	18     	15  	 
/api/v1/products/     	23     	70     	11     	18     	18  	 
/api/v1/shipping/     	60     	128    	26     	32     	25  	 
                        178    	494    	96     	116    	116
```


## Licence

Author: Stanislav Rubtsov