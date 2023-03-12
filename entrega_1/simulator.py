import sys
import os
import simulator
import pandas as pd
import pytz
import datetime as dt
import shutil

def choose_seed_file():
    path = os.path.isdir('simulator_file')
    route = os.path.dirname(__file__)
    #print(path): pendiente preguntar esta duda.¿Por que un print crea una variable de manera global?
    last_file_created = []
    if path == True:
        files = os.listdir('simulator_file')
        if files == []:
            os.rmdir('simulator_file')
        else:
            last_file_created = sorted(files, reverse=True)[0]
            print(f"{last_file_created} is file for simulator")
        route_calculate = str(route)+ "/simulator_file/" + str(last_file_created)
        
        ##print(type(route_calculate))

    else:
        os.mkdir(route+"/simulator_file")
    
        route_calculate = route+"/trabajo.csv"
        print(f"file has been created in route: {route_calculate}")
    return route_calculate

def open_database_file():
    filename = choose_seed_file()
    data = pd.read_csv(filename, sep=",")
    print(f"File upload is {type(data)}")
    return data


#FUNCION DE LIMPIEZA SOBRE EL ARCHIVO MATRIZ
def data_proccess():

    data = open_database_file()
    
    data.fillna(value=0, inplace=True)
    data.replace([float('inf'), float('-inf')], 0, inplace=True)

    data_clean = data.astype({'main_user_id':'int','validation_state':'str', 'town': 'str', 'state':'str', 'item_post':'int', 'wishes':'int', 'count_total_transactions':'int','count_swaps':'int', 'count_sales':'int', 'swap_offers_sent':'int', 'accepted':'int','rejected':'int', 'expired':'int', 'canceled':'int', 'days_online':'int'})

    data_clean.last_seen = pd.to_datetime(data.last_seen)
    data_clean.last_login = pd.to_datetime(data.last_login)
    ##data_clean = data_clean.drop(columns=['user_id'], axis =1)
    data_clean.town.replace('0','', inplace=True)
    data_clean.state.replace('0','', inplace=True)
    data_clean.validation_state.replace('0','', inplace=True)
    data_clean = data_clean.drop(data_clean.loc[data_clean["main_user_id"] == 0].index)

    route = os.path.dirname(__file__)
    ruta_destino = str(route)+'/simulator_file/copy_duplicate_2.csv' # reemplazar copy por str(now())
    data_clean.to_csv(ruta_destino, index=False)
    return data_clean

#FUNCION QUE COPIA DEL ARCHIVO PRINCIPAL LIMPIO  PARA GENERAR LA SIMULACION
def copy_data():

    data_clean = data_proccess()
    duplicate = data_clean.copy()
    #print(duplicate)
    return duplicate

# SELECCION DE ELEGIBLES: USUARIOS CON item_post AND wishes != 0
def the_choosen_ones():
    
    duplicate = copy_data()
    non_select_users = duplicate[ (duplicate['item_post'] == 0 ) | (duplicate['wishes'] == 0) ].index
    duplicate.drop(non_select_users, inplace= True)
    #print(duplicate)
    #print(duplicate['item_post'], duplicate['wishes'])
    return duplicate

# FUNCION PARA CALCULAR EL PRODUCT_OPS
def product_ops_1():

    duplicate = the_choosen_ones()
    duplicate['product_ops'] = duplicate['item_post'] / duplicate['wishes']
    return duplicate

# FUNCION PARA CLASIFICAR AL USUARIO SEGUN LA RELACION ITEMS PUBLICADOS Y WISHES
def classification():

    duplicate = product_ops_1() 

    def evaluar_condicion(product_ops):
        if product_ops < 0.8 :
            return 'Buyer'
        elif product_ops >= 0.8 and  product_ops < 1.2:
            return 'Swapper'
        else:
            return 'Seller'

    duplicate['classification'] = duplicate['product_ops'].apply(evaluar_condicion)
    #print(duplicate)
    return duplicate

#FUNCION QUE SELECCIONA 800 USUARIOS ALEATORIAMENTE Y LES ASIGNA EL ROL: 1 -> ENVIA LA OFERTA 0 -> RECIBE LA OFERTA, TOMA LA DECISION
def select_random_users(n):

    duplicate = classification()

    random_users = duplicate.sample(n)

    values = [1, 0] * (len(random_users) // 2)
    if len(random_users) % 2 == 1:
        values.append(1)
    random_users['role'] = values
    
    return random_users

#FUNCION PARA CREAR LAS PAREJAS TRANSACCIONALES
def transactional_tuples(n):

    random_users = select_random_users(n)
    duplicated_num = []
    for i in range(1, int(n/2)+1):
        duplicated_num.extend([i]*2)

    random_users['group'] = duplicated_num[:n]
    return random_users

#FUNCION PARA CREAR LA COLUMNA 'decision' y resetear el index de la tabla
def decision_assigment(n):

    random_users = transactional_tuples(n)
    random_users['decision'] =''

    random_users = random_users.reset_index()
    #print(random_users)
    return random_users

#FUNCION PARA ASIGNAR LA DECISION DE QUIEN RECIBE LA OFERTA
def decision_assesment(n): 

    random_users = decision_assigment(n)
    i = 1
    for j in range(1,int(n/2)+1):
        
        #print(random_users['role'][i])
        #print(random_users['classification'][i])
        #print(random_users['accepted'][i]),print(random_users['rejected'][i]),print(random_users['expired'][i]),print(random_users['canceled'][i])
        if random_users['role'][i-1] == 1 and random_users['classification'][i-1] == 'Swapper':
           random_users.at[i-1,'swap_offers_sent'] = random_users['swap_offers_sent'][i-1] + 1
        if random_users['role'][i] == 0 and random_users['classification'][i] == 'Swapper':
            random_users.at[i,'decision'] = 'accepted'   
            random_users.at[i,'accepted'] =  random_users['accepted'][i] + 1  
        elif random_users['role'][i] == 0 and random_users['classification'][i] == 'Buyer': 
            random_users.at[i,'decision'] = 'accepted'   
            random_users.at[i,'accepted'] =  random_users['accepted'][i] + 1 
        elif random_users['role'][i] == 0 and random_users['classification'][i] == 'Seller':
            random_users.at[i,'decision'] = 'rejected'   
            random_users.at[i,'rejected'] =  random_users['rejected'][i] + 1 
        elif random_users['role'][i- 1] == 1 and random_users['classification'][i - 1] == 'Buyer':
            random_users.at[i-1,'swap_offers_sent'] = random_users['swap_offers_sent'][i-1] + 1
            if random_users['role'][i] == 0 and random_users['classification'][i] == 'Swapper':
                random_users.at[i,'decision'] = 'accepted'   
                random_users.at[i,'accepted'] =  random_users['accepted'][i] + 1
            elif random_users['role'][i] == 0 and random_users['classification'][i] == 'Buyer': 
                random_users.at[i,'decision'] = 'rejected'   
                random_users.at[i,'rejected'] =  random_users['rejected'][i] + 1 
            elif random_users['role'][i] == 0 and random_users['classification'][i] == 'Seller':
                random_users.at[i,'decision'] = 'rejected'   
                random_users.at[i,'rejected'] =  random_users['rejected'][i] + 1 
        elif random_users['role'][i - 1] == 1 and random_users['classification'][i-1 ] == 'Seller':  
            random_users.at[i-1,'swap_offers_sent'] = random_users['swap_offers_sent'][i-1] + 1
            if random_users['role'][i] == 0  and random_users['classification'][i] == 'Swapper':
                random_users.at[i,'decision'] = 'accepted'   
                random_users.at[i,'accepted'] =  random_users['accepted'][i] + 1
            elif random_users['role'][i] == 0 and random_users['classification'][i] == 'Buyer': 
                random_users.at[i,'decision'] = 'expired'   
                random_users.at[i,'expired'] =  random_users['expired'][i] + 1
            elif random_users['role'][i] == 0 and random_users['classification'][i] == 'Seller':
                random_users.at[i,'decision'] = 'canceled'   
                random_users.at[i,'canceled'] =  random_users['canceled'][i] + 1
        
        i = (j * 2) + 1
    
    #print(random_users[random_users['group'] == i + 1].main_user_id)
    #print(random_users)
    return random_users

# FUNCION PARA ACTUALIZAR LA COLUMNA last_seen A LA FECHA ACTUAL
def offers_simulated_dataframe(n,t):

    random_users= decision_assesment(n)

    #tz = pytz.timezone('America/Bogota')
    random_users['last_seen'] = t #dt.datetime.now(tz).date()
    offers_simulated = random_users
    #print(offers_simulated)
    return offers_simulated

#Funcion que actualiza los registros de los random_users en el archivo semilla.

def update_offers_day(n,t):
    
    #leer er archivo duplicado con pandas antes de usarlo en la funcion que nos entrega la ruta 

    offers_simulated = offers_simulated_dataframe(n,t)

    route = os.path.dirname(__file__)
    ruta_destino = str(route)+'/simulator_file/copy_duplicate_2.csv'
    file = pd.read_csv(ruta_destino, sep=",")

    offers_cols = ['main_user_id', 'last_seen', 'swap_offers_sent', 'accepted', 'rejected', 'expired', 'canceled']
    offers_renamed = offers_simulated[offers_cols].rename(columns={col: f"offer_{col}" for col in offers_cols[1:]})

    merged_df = pd.merge(file, offers_renamed, left_on='main_user_id', right_on='main_user_id', how="left")

    cols_to_update = ['last_seen', 'swap_offers_sent', 'accepted', 'rejected', 'expired', 'canceled']
    for col in cols_to_update:
        merged_df[col] = merged_df[f"offer_{col}"].fillna(merged_df[col])

    merged_df = merged_df.drop(columns=[f"offer_{col}" for col in cols_to_update])
    merged_df = merged_df.rename(columns={f"offer_{col}": col for col in cols_to_update})
    
    merged_df.last_seen = pd.to_datetime(merged_df.last_seen)
    print(type(merged_df.last_seen))
    merged_df.sort_values(by = 'last_seen', ascending=False, inplace = True)

    return merged_df


## FUNCION PARA GUARDAR EL RESULTADO DE LA SIMULACION EN LA CARPETA simulator_file

def save_simulation(n,t):

    merged_df = update_offers_day(n,t)

    #tz = pytz.timezone('America/Bogota')
    date_simulation = t.strftime('%Y-%m-%d')


    route = os.path.dirname(__file__)
    ruta_destino = str(route)+'/simulator_file/'+ str(date_simulation)+'_duplicate_2.csv' # reemplazar copy por str(now())
    merged_df.to_csv(ruta_destino, index=False)
    print(f"La simulacion para el dia {date_simulation} ha finalizado con exito")
    print(merged_df)



## FUNCION PARA VALIDAR SI EL N ES PAR 
def pair_number_verify(n,t):
    if n%2 == 0:
        save_simulation(n,t)
    else:
        print('You must input even number please')


##FUNCION PARA DEFINIR LA FECHA DE CORRIDA DE LA SIMULACION
def simulation_date_run(n=800,t="2023-04-04"):
     tz = pytz.timezone('America/Bogota')
    
     if t == 0:
         t = dt.datetime.now(tz).date()
         print(f"Aca imprime la fecha del sistema que es: {t}")
         save_simulation(n,t)
     else:
         t = dt.datetime(sys.argv[1])
         print(f"Aca imprime la fecha ingresada: {t}")
         save_simulation(n,t)

