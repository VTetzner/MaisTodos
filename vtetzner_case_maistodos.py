#!/usr/bin/env python
# coding: utf-8

# # Bibliotecas

# In[9]:


get_ipython().system('pip install numpy')
get_ipython().system('pip install pandas')

import pandas as pd
import numpy as np
from zipfile import ZipFile


# # Leitura de tabela

# In[10]:


with ZipFile('teste_tecnico.zip', 'r') as zipObj:
   # Extract all the contents of zip file in current directory
   zipObj.extractall()
tabela = pd.read_csv('teste_tecnico.csv') #Inserir PATH do arquivo *.CSV


# In[3]:


## Organiza a tabela por data de pagamento
tabela_data_pagamento = tabela.sort_values('payment_date')
tabela_data_pagamento.index = pd.RangeIndex(start=0, stop=len(tabela_data_pagamento), step=1)


# # Problema 1
# 
# Qual o dia de pagamento de melhor conversão (transações autorizadas X total)
# 
# transações autorizadas: payment_authorized == 1
# 
# total: soma do total do dia (contando não autorizados)

# In[7]:


## Transações autorizadas
pagamento_autorizado = tabela_data_pagamento['payment_authorized']==1
tabela_pagamento_autorizado = tabela_data_pagamento[pagamento_autorizado]
tabela_pagamento_autorizado.index = pd.RangeIndex(start=0, stop=len(tabela_pagamento_autorizado), step=1)

## Contagem de transações autorizados por dia
cont_pagamento_autorizado = tabela_pagamento_autorizado['payment_date'].value_counts().to_frame(name='cont_pagamento_autorizado').sort_index()

## Vetor dos dias na tabela
dia = tabela_data_pagamento['payment_date'].unique()
dia_df = pd.DataFrame(dia, columns=['dia'])

## Iteração para somatoria do total de pagamento (autorizado + não autorizado)
total_por_dia =[]

for i in range(len(dia)):
  soma = 0
  ##print('Dia: ', i)

  for j in range(len(tabela_data_pagamento)):
    if tabela_data_pagamento['payment_date'][j] == dia[i]:
      soma += tabela_data_pagamento['payment_amount'][j]

    else:
      pass
  total_por_dia.append(soma)

## Total diario
total_dia_soma = pd.DataFrame(total_por_dia, columns=['total_diario'])

## Junções de DataFrames
df_dia_valorTotal = pd.concat([dia_df, total_dia_soma], axis=1).set_index('dia').sort_index()

df_dia_valorTotal_autorizadas = pd.concat([df_dia_valorTotal, cont_pagamento_autorizado], axis=1)
df_dia_valorTotal_autorizadas['conversao'] = df_dia_valorTotal_autorizadas['total_diario'] * df_dia_valorTotal_autorizadas['cont_pagamento_autorizado']
df_dia_valorTotal_autorizadas = df_dia_valorTotal_autorizadas.sort_values('conversao', ascending=False)

dia_max_conversao = df_dia_valorTotal_autorizadas.index[0]


# In[ ]:


print('O dia de maior conversão foi: ', dia_max_conversao)


# # Problema 2
# 
# Qual foi a conversão desses meses? 
# 
# (% de assinaturas com transações autorizadas por periodos (mes))
# 
# mes -> ciclo (12 ciclos)
# 
# total -> tabela inteira
# 
# autorizadas -> tabela pay_aut ==1

# In[ ]:


## Ciclos
ciclos = tabela_data_pagamento['cycle_id'].unique()
ciclos_df = pd.DataFrame(ciclos, columns=['Mes'])

## Contagem de ciclos -- Todas as transações (autorizadas e não autorizadas)
cont_ciclos_total = tabela_data_pagamento['cycle_id'].value_counts().to_frame(name='cont_ciclos_totais').sort_index()
cont_ciclos_total.index = pd.RangeIndex(start=0, stop=len(cont_ciclos_total), step=1)

## Contagem de ciclos -- Transações autorizadas
cont_ciclos_autorizados = tabela_pagamento_autorizado['cycle_id'].value_counts().to_frame(name='cont_ciclos_autorizados').sort_index()
cont_ciclos_autorizados.index = pd.RangeIndex(start=0, stop=len(cont_ciclos_autorizados), step=1)

## Porcentagem
ciclos_df['Conversao [%]'] = (cont_ciclos_autorizados['cont_ciclos_autorizados']/cont_ciclos_total['cont_ciclos_totais'])*100
porcentagem_conversao_mes = ciclos_df.set_index(['Mes'])

## Visualização
print('Porcentagem de conversao por mes: ', porcentagem_conversao_mes)


# # Problema 3
# 
# Qual foi a arrecadacao de todas as retentativas(payment_attempt > 1) X periodo (Mes)
# 
# Corrigido para pay_att > 1 (ou >0?)
# 
# Utiliza **pagamentos autorizados**

# In[ ]:


## Tabela de retentativas
tabela_retentativa = tabela_pagamento_autorizado[tabela_pagamento_autorizado.payment_attempt > 1]
tabela_retentativa.index = pd.RangeIndex(start=0, stop=len(tabela_retentativa), step=1)

## Tabela de meses
mes_df = pd.DataFrame(ciclos, columns=['Mes'])

## Iteração para somatoria do total de pagamento por mes de retentativas
total_por_mes =[]

for i in range(len(ciclos)):
  soma = 0
  for j in range(len(tabela_retentativa)):
    if tabela_retentativa['cycle_id'][j] == ciclos[i]:
      soma += tabela_retentativa['payment_amount'][j]
    else:
      pass
  total_por_mes.append(soma)

## Total mensal de retentativas
total_mes_soma = pd.DataFrame(total_por_mes, columns=['Total_Mensal_Retentativas'])

## Junções de DataFrames
df_mes_valorTotal = pd.concat([mes_df, total_mes_soma], axis=1).set_index('Mes').sort_index()

## Visualização
print('Total mensal de retentativas por mes: ', df_mes_valorTotal)


# # Problema 4
# 
# Considerando as taxas: cielo com 0,05, a rede 0,065, adyen 0,123, pagseguro 0,04. Qual processadora é mais rentável para o sistema considerando valor arrecadado e pago

# In[ ]:


## Processadoras
processadora = tabela_data_pagamento['payment_processor'].unique()
processadora_df = pd.DataFrame(processadora, columns=['Processadora'])

## Taxas
taxas = {'rede': 0.065, 'pagseguro': 0.04, 'adyen': 0.123, 'cielo':0.05}

## Iteração para somatoria do total de pagamento por operadora de pagamentos autorizados
total_por_processadora =[]

for i in range(len(processadora)):
  soma = 0
  for j in range(len(tabela_pagamento_autorizado)):
    if tabela_pagamento_autorizado['payment_processor'][j] == processadora[i]:
      soma += tabela_pagamento_autorizado['payment_amount'][j]
    else:
      pass
  total_por_processadora.append(soma)

df_total_por_processadora = pd.DataFrame(total_por_processadora, columns=['montante_por_processadora'])

## Junções de DataFrames
df_processadora_valorTotal = pd.concat([processadora_df, df_total_por_processadora], axis=1)  #.set_index('Operadoras').sort_index()
df_processadora_valorTotal['taxa'] = df_processadora_valorTotal['Processadora'].map(taxas)  # Puxa a taxa do dicionário
tabela_rentabilidade_por_taxa = df_processadora_valorTotal.set_index('Processadora').sort_index()

## Rentabilidade da empresa em cima da taxa das operadoras, considerando os pagamentos autorizados
tabela_rentabilidade_por_taxa['rentabilidade_empresa'] = tabela_rentabilidade_por_taxa['montante_por_processadora'] * (1 - tabela_rentabilidade_por_taxa['taxa'])

## Organiza pela maior rentabilidade e devolve a processadora que é mais rentavel
tabela_rentabilidade_por_taxa = tabela_rentabilidade_por_taxa.sort_values('rentabilidade_empresa', ascending=False)
operadora_max_rentabilidade = tabela_rentabilidade_por_taxa.index[0]

## Visualização
print('Tabela de rentabilidade por taxa para cada processadora: ', tabela_rentabilidade_por_taxa)


# In[ ]:


print('A processadora mais rentavel para o sistema considerando os pagamentos autorizados é: ', operadora_max_rentabilidade)


# # Problema 5
# 
# Qual foi a retentativa(payment_attempt > 1) e processadora que mais converteram
# 
# Maior conversao é da pagseguro (vide problema 4)
# 
# Encontraremos qual é a retentativa agora que mais trouxe maior conversão
# 
# **Aqui poderia ter sido programado uma função para entrada das tabelas, tenho apenas um código de loop, deixando o código mais limpo. O mesmo se aplica para trabalhar com dicionarios para a chama dos nomes das processadoras, e então reduzindo mais linhas e consequentemente tempo computacional**

# In[ ]:


## Tabelas gerais
tabela_retentativa_conversao = tabela_data_pagamento[tabela_data_pagamento.payment_attempt > 1]
tabela_retentativa_conversao.index = pd.RangeIndex(start=0, stop=len(tabela_retentativa_conversao), step=1)

retentativa_autorizada = tabela_retentativa_conversao['payment_authorized']==1
tabela_retentativa_autorizado = tabela_retentativa_conversao[retentativa_autorizada]
tabela_retentativa_autorizado.index = pd.RangeIndex(start=0, stop=len(tabela_retentativa_autorizado), step=1)


# In[ ]:


## Retentativas
retentativas = tabela_retentativa_conversao['payment_attempt'].unique()
retentativas_df = pd.DataFrame(retentativas, columns=['Retentativas'])
retentativas_df.index = pd.RangeIndex(start=0, stop=len(retentativas_df), step=1)


# In[ ]:


######## PAGSEGURO

## Tabela da pagseguro
pagseguro = tabela_data_pagamento['payment_processor']=='pagseguro'
tabela_pagseguro = tabela_data_pagamento[pagseguro]
tabela_pagseguro_retentativa = tabela_pagseguro[tabela_pagseguro.payment_attempt > 1]
tabela_pagseguro_retentativa.index = pd.RangeIndex(start=0, stop=len(tabela_pagseguro_retentativa), step=1)

## Tabela da pagseguro com pagamentos autorizados
pagseguro_autorizado = tabela_pagseguro_retentativa['payment_authorized']==1
tabela_pagseguro_autorizado = tabela_pagseguro_retentativa[pagseguro_autorizado]
tabela_pagseguro_autorizado.index = pd.RangeIndex(start=0, stop=len(tabela_pagseguro_autorizado), step=1)

## Iteração para somatoria do total de pagamento por transação autorizado e NÃO autorizada, pela pagseguro, para cada retentativa
total_ps_retentativa =[]

for i in range(len(retentativas_df)):
  soma = 0
  for j in range(len(tabela_pagseguro_retentativa)):
    if tabela_pagseguro_retentativa['payment_attempt'][j] == retentativas_df['Retentativas'][i]:
      soma += tabela_pagseguro_retentativa['payment_amount'][j]
    else:
      pass
  total_ps_retentativa.append(soma)
ps_ret = pd.DataFrame(total_ps_retentativa, columns=['ps'])

## Iteração para somatoria do total de pagamento por transação autorizado, pela pagseguro, para cada retentativa
total_ps_autorizada_retentativa = []

for i in range(len(retentativas_df)):
  soma = 0
  for j in range(len(tabela_pagseguro_autorizado)):
    if tabela_pagseguro_autorizado['payment_attempt'][j] == retentativas_df['Retentativas'][i]:
      soma += tabela_pagseguro_autorizado['payment_amount'][j]

    else:
      pass
  total_ps_autorizada_retentativa.append(soma)
ps_auto_ret = pd.DataFrame(total_ps_autorizada_retentativa, columns=['ps_autorizada'])


# In[ ]:


######## REDE

## Tabela da rede
rede = tabela_data_pagamento['payment_processor']=='rede'
tabela_rede = tabela_data_pagamento[rede]
tabela_rede_retentativa = tabela_rede[tabela_rede.payment_attempt > 1]
tabela_rede_retentativa.index = pd.RangeIndex(start=0, stop=len(tabela_rede_retentativa), step=1)

## Tabela da rede com pagamentos autorizados
rede_autorizado = tabela_rede_retentativa['payment_authorized']==1
tabela_rede_autorizado = tabela_rede_retentativa[rede_autorizado]
tabela_rede_autorizado.index = pd.RangeIndex(start=0, stop=len(tabela_rede_autorizado), step=1)

## Iteração para somatoria do total de pagamento por transação autorizado e NÃO autorizada, pela pagseguro, para cada retentativa
total_rede_retentativa =[]

for i in range(len(retentativas_df)):
  soma = 0

  for j in range(len(tabela_rede_retentativa)):
    if tabela_rede_retentativa['payment_attempt'][j] == retentativas_df['Retentativas'][i]:
      soma += tabela_rede_retentativa['payment_amount'][j]
    else:
      pass
  total_rede_retentativa.append(soma)
rede_ret = pd.DataFrame(total_rede_retentativa, columns=['rede'])

## Iteração para somatoria do total de pagamento por transação autorizado, pela pagseguro, para cada retentativa
total_rede_autorizada_retentativa = []

for i in range(len(retentativas_df)):
  soma = 0
  for j in range(len(tabela_rede_autorizado)):
    if tabela_rede_autorizado['payment_attempt'][j] == retentativas_df['Retentativas'][i]:
      soma += tabela_rede_autorizado['payment_amount'][j]
    else:
      pass
  total_rede_autorizada_retentativa.append(soma)
rede_auto_ret = pd.DataFrame(total_rede_autorizada_retentativa, columns=['rede_autorizada'])


# In[ ]:


######## CIELO

## Tabela da cielo
cielo = tabela_data_pagamento['payment_processor']=='cielo'
tabela_cielo = tabela_data_pagamento[cielo]
tabela_cielo_retentativa = tabela_cielo[tabela_cielo.payment_attempt > 1]
tabela_cielo_retentativa.index = pd.RangeIndex(start=0, stop=len(tabela_cielo_retentativa), step=1)

## Tabela da rede com pagamentos autorizados
cielo_autorizado = tabela_cielo_retentativa['payment_authorized']==1
tabela_cielo_autorizado = tabela_cielo_retentativa[cielo_autorizado]
tabela_cielo_autorizado.index = pd.RangeIndex(start=0, stop=len(tabela_cielo_autorizado), step=1)

## Iteração para somatoria do total de pagamento por transação autorizado e NÃO autorizada, pela pagseguro, para cada retentativa
total_cielo_retentativa =[]

for i in range(len(retentativas_df)):
  soma = 0

  for j in range(len(tabela_cielo_retentativa)):
    if tabela_cielo_retentativa['payment_attempt'][j] == retentativas_df['Retentativas'][i]:
      soma += tabela_cielo_retentativa['payment_amount'][j]
    else:
      pass
  total_cielo_retentativa.append(soma)
cielo_ret = pd.DataFrame(total_cielo_retentativa, columns=['cielo'])

## Iteração para somatoria do total de pagamento por transaçãovou  autorizado, pela pagseguro, para cada retentativa
total_cielo_autorizada_retentativa = []

for i in range(len(retentativas_df)):
  soma = 0

  for j in range(len(tabela_cielo_autorizado)):
    if tabela_cielo_autorizado['payment_attempt'][j] == retentativas_df['Retentativas'][i]:
      soma += tabela_cielo_autorizado['payment_amount'][j]
    else:
      pass
  total_cielo_autorizada_retentativa.append(soma)
cielo_auto_ret = pd.DataFrame(total_cielo_autorizada_retentativa, columns=['cielo_autorizada'])


# In[ ]:


######## ADYEN

## Tabela da adyen
adyen = tabela_data_pagamento['payment_processor']=='adyen'
tabela_adyen = tabela_data_pagamento[adyen]
tabela_adyen_retentativa = tabela_adyen[tabela_adyen.payment_attempt > 1]
tabela_adyen_retentativa.index = pd.RangeIndex(start=0, stop=len(tabela_adyen_retentativa), step=1)

## Tabela da adyen com pagamentos autorizados
adyen_autorizado = tabela_adyen_retentativa['payment_authorized']==1
tabela_adyen_autorizado = tabela_adyen_retentativa[adyen_autorizado]
tabela_adyen_autorizado.index = pd.RangeIndex(start=0, stop=len(tabela_adyen_autorizado), step=1)

## Iteração para somatoria do total de pagamento por transação autorizado e NÃO autorizada, pela pagseguro, para cada retentativa
total_adyen_retentativa =[]

for i in range(len(retentativas_df)):
  soma = 0
  for j in range(len(tabela_adyen_retentativa)):
    if tabela_adyen_retentativa['payment_attempt'][j] == retentativas_df['Retentativas'][i]:
      soma += tabela_adyen_retentativa['payment_amount'][j]
    else:
      pass
  total_adyen_retentativa.append(soma)
adyen_ret = pd.DataFrame(total_adyen_retentativa, columns=['adyen'])

## Iteração para somatoria do total de pagamento por transaçãovou  autorizado, pela pagseguro, para cada retentativa
total_adyen_autorizada_retentativa = []

for i in range(len(retentativas_df)):
  soma = 0
  for j in range(len(tabela_adyen_autorizado)):
    if tabela_adyen_autorizado['payment_attempt'][j] == retentativas_df['Retentativas'][i]:
      soma += tabela_adyen_autorizado['payment_amount'][j]
    else:
      pass
  total_adyen_autorizada_retentativa.append(soma)
adyen_auto_ret = pd.DataFrame(total_adyen_autorizada_retentativa, columns=['adyen_autorizada'])


# In[ ]:


## Conversão
conversao_ret_proc = retentativas_df.copy()
conversao_ret_proc['pagseguro'] = (ps_auto_ret['ps_autorizada']/ps_ret['ps'])*100
conversao_ret_proc['cielo'] = (cielo_auto_ret['cielo_autorizada']/cielo_ret['cielo'])*100
conversao_ret_proc['rede'] = (rede_auto_ret['rede_autorizada']/rede_ret['rede'])*100
conversao_ret_proc['adyen'] = (adyen_auto_ret['adyen_autorizada']/adyen_ret['adyen'])*100
conversao_ret_proc_final = conversao_ret_proc.copy()
conversao_ret_proc_final = conversao_ret_proc_final.set_index(['Retentativas'])
conv_proc_max = max(conversao_ret_proc_final)
conv_ret_max = conversao_ret_proc_final.idxmax(axis='index')


# In[ ]:


print('A processadora que mais converteu foi a ', conv_proc_max, ' na retentativa número ', conv_ret_max[conv_proc_max])
print('\n')
print(conversao_ret_proc_final)


# # Problema 6
# 
# Qual foi o payment_code com maior aprovação em retentativas (payment_atttempt > 0)
# [0 1 AC BC EE]

# In[ ]:


## Tabelas RETENTATIVAS
tabela_retentativa = tabela_data_pagamento[tabela_data_pagamento.payment_attempt > 0]
tabela_retentativa.index = pd.RangeIndex(start=0, stop=len(tabela_retentativa), step=1)
retentativa_autorizada = tabela_retentativa['payment_authorized']==1
tabela_retentativa_autorizado = tabela_retentativa[retentativa_autorizada]
tabela_retentativa_autorizado.index = pd.RangeIndex(start=0, stop=len(tabela_retentativa_autorizado), step=1)

## Códigos de pagamento
pay_code = tabela_retentativa['payment_code'].unique()
pay_code_df = pd.DataFrame(pay_code, columns=['payment_code'])
pay_code_df.index = pd.RangeIndex(start=0, stop=len(pay_code_df), step=1)

## Iteração para somatoria do total de pagamento por mes de retentativas
total_por_code =[]

for i in range(len(pay_code)):
  soma = 0

  for j in range(len(tabela_retentativa_autorizado)):
    if tabela_retentativa_autorizado['payment_code'][j] == pay_code[i]:
      soma += 1

    else:
      pass
  total_por_code.append(soma)

total_por_code_df = pd.DataFrame(total_por_code, columns=['numero_de_autorizacoes'])
tabela_final_payCode_ret=0
tabela_final_payCode_ret = pd.concat([pay_code_df, total_por_code_df],axis=1).set_index(['payment_code'])

codigo_max = tabela_final_payCode_ret.idxmax(axis='index')

print('O código de pagamento com maior aprovação em retentativas (payment_attempt>0) foi: ', codigo_max[max(tabela_final_payCode_ret)], '\n')
print(tabela_final_payCode_ret)


# # Problema 7
# 
# Qual foi o payment_code com menor aprovação em retentativas

# In[ ]:


## Tabelas RETENTATIVAS
tabela_retentativa = tabela_data_pagamento[tabela_data_pagamento.payment_attempt > 0]
tabela_retentativa.index = pd.RangeIndex(start=0, stop=len(tabela_retentativa), step=1)
retentativa_n_autorizada = tabela_retentativa['payment_authorized']==0
tabela_retentativa_n_autorizado = tabela_retentativa[retentativa_n_autorizada]
tabela_retentativa_n_autorizado.index = pd.RangeIndex(start=0, stop=len(tabela_retentativa_n_autorizado), step=1)

## Códigos de pagamento
pay_code = tabela_retentativa['payment_code'].unique()
pay_code_df = pd.DataFrame(pay_code, columns=['payment_code'])
pay_code_df.index = pd.RangeIndex(start=0, stop=len(pay_code_df), step=1)

## Iteração para somatoria do total de pagamento por mes de retentativas
total_por_code =[]

for i in range(len(pay_code)):
  soma = 0

  for j in range(len(tabela_retentativa_n_autorizado)):
    if tabela_retentativa_n_autorizado['payment_code'][j] == pay_code[i]:
      soma += 1

    else:
      pass
  total_por_code.append(soma)

total_por_code_df = pd.DataFrame(total_por_code, columns=['numero_de_n_autorizacoes'])
tabela_final_payCode_ret=0
tabela_final_payCode_ret = pd.concat([pay_code_df, total_por_code_df],axis=1).set_index(['payment_code'])

codigo_max = tabela_final_payCode_ret.idxmax(axis='index')

print('O código de pagamento com menor aprovação em retentativas (payment_attempt>0) foi: ', codigo_max[max(tabela_final_payCode_ret)], '\n')
print(tabela_final_payCode_ret)


# # Problema 8
# 
# Qual o melhor dia de pagamento por payment_attempt
# 
# 
# Analisado os números de retentativas, qual é o melhor dia de pagamento por quantidade de retentativas?
# 
# **pagamentos autorizados**

# In[ ]:


## Tabelas AUTORIZADA
# tabela_retentativa = tabela_data_pagamento[tabela_data_pagamento.payment_attempt > 0]
# tabela_retentativa.index = pd.RangeIndex(start=0, stop=len(tabela_retentativa), step=1)
pagamento_autorizado = tabela_data_pagamento['payment_authorized']==1
tabela_autorizado = tabela_data_pagamento[pagamento_autorizado]
tabela_autorizado.index = pd.RangeIndex(start=0, stop=len(tabela_autorizado), step=1)

## Retentativas
retentativas = tabela_autorizado['payment_attempt'].unique()
retentativas_df = pd.DataFrame(retentativas, columns=['Retentativas'])
retentativas_df.index = pd.RangeIndex(start=0, stop=len(retentativas_df), step=1)
#retentativas_df

## Contagem de transações autorizados por dia
cont_autorizado = tabela_autorizado['payment_date'].value_counts().to_frame(name='cont_autorizado').sort_index()

## Vetor dos dias na tabela
dia_8 = tabela_autorizado['payment_date'].unique()
dia_8_df = pd.DataFrame(dia_8, columns=['dia'])
dia_8_df

## Contagem de retentativas por dia

## Iteração para somatoria do total de pagamento (autorizado + não autorizado)
cont_retentativa_por_dia =[]
numero_retentativa = []

for i in range(len(dia_8)):
  soma = 0

  for j in range(len(tabela_autorizado)):
    if tabela_autorizado['payment_date'][j] == dia_8[i]:
      numero_retentativa.append(tabela_autorizado['payment_attempt'][j])

    else:
      pass
  retentativas_por_dia = np.unique(np.array(numero_retentativa))
  cont_retentativa_por_dia.append(len(retentativas_por_dia))

cont_retentativa_por_dia_df = pd.DataFrame(cont_retentativa_por_dia, columns=['numero_de_retentativas'])

tabela_final_8 = cont_autorizado.copy()
tabela_final_8['numero_de_retentativas'] = cont_retentativa_por_dia
tabela_final_8['pagamento/#_retentativa'] = tabela_final_8['cont_autorizado']/tabela_final_8['numero_de_retentativas']
melhor_valor = max(tabela_final_8['pagamento/#_retentativa'])
melhor_dia = tabela_final_8.index[tabela_final_8['pagamento/#_retentativa']==melhor_valor].tolist()

print('O melhor dia de pagamento, por quantidade de retentativas, foi: ', melhor_dia )
