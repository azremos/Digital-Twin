import csv
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
from scipy.fft import fft, fftfreq
import pandas as pd
import keras
import tensorflow as tf
import os
from openpyxl import load_workbook, Workbook

Lien_dossier = "C:/Users/Antoine Daguerre/Downloads/FINAL RECONNAISSANCE"

catégorie = ["neuf","déséquilibré","érraflé"]

def traitement_xlsx_to_csv(path):
    wb = load_workbook(Lien_dossier+"/" + path)
    ws = wb['Sheet1']
    ws.delete_rows(1,2)
    ws.delete_cols(1,1)
    wb.save(Lien_dossier+"/" + path)
    read_file = pd.read_excel(Lien_dossier+"/" + path)
    read_file.to_csv(Lien_dossier+"/" + path[:-4] + "csv")
    os.remove(Lien_dossier+"/" + path)

def traitement_dossier_xlsx_to_csv():
    for path in os.listdir(Lien_dossier):
        if(path.endswith(".xlsx")):
            print(path)
            traitement_xlsx_to_csv(path)

def random_tranche(N,X,Y):
    L = len(X)
    x0 = np.random.randint(0,L+1-N)
    return(X[x0:x0+N],Y[x0:x0+N])


def remplir(Courbes):
    for nom in([("test23_",[1,0,0]),("test24_",[0,1,0]),("test25_",[0,1,0]),("test29_",[0,0,1]),("test31_",[0,0,1]),("test33_",[0,0,1]),("test35_",[0,0,1]),("test39_",[0,0,1]),("test37_",[0,0,1])]):
        for j in range(1,5):
            print(j)
            with open(Lien_dossier+"/"+nom[0]+str(j)+'.csv', newline='') as f:
                reader = csv.reader(f)
                data = [tuple(row) for row in reader]
            X,Y=[],[]

            for i in range(2,len(data)):
                if(len(data[i])> 2):
                    data[i] = data[i][-2:]
                (x,y)=data[i]
                x=float(x)
                y=float(y)
                X.append(x)
                Y.append(y)

            X,Y=np.array(X),np.array(Y)
            Y=Y-np.mean(Y)
            # Number of samples in normalized_tone

            for i in range(30):
                X2,Y2 = random_tranche(len(X)//2,X,Y)
                SAMPLE_RATE= np.mean([X2[k+1]-X2[k] for k in range(len(X2)-1)])
                DURATION= X2[len(X2)-1]-X[0]
                N = len(X2)
                yf = fft(Y2)
                yf = np.abs(yf)
                xf = fftfreq(N, SAMPLE_RATE)
                xf,yf = xf[0:len(xf)//2],yf[0:len(yf)//2]
                Courbes.append(xf)
                Courbes.append(yf)
                Courbes.append(nom[1])
                #plt.plot(xf,yf,linewidth=0.4)
                #plt.title(nom[0]+str(j))
                #plt.show()
            #plt.title(nom[0] + str(j))
            #plt.show()



def fixer_nbr_point_fonction(X,Y,n_points,x_min,x_max):
    x = x_min
    X2 = []
    Y2 = []
    e = np.mean([X[k+1]-X[k] for k in range(len(X)-1)])
    i = 0
    while(i<n_points):
        i+=1
        X2.append(x)
        k = (x-X[0])/e
        k_int = int(k)
        if(k>=len(X)-1):
            Y2.append(Y[k_int])
        else:
            Y2.append((Y[k_int]+ (k-k_int)*(Y[k_int+1]-Y[k_int])))
        x += (x_max-x_min)/(n_points-1)
    return(X2,Y2)


def nb_point_to(L,x_max):
    k = 1
    while(L[k-1]<x_max and k<len(L)-1):
        k+=1
    return(k)

def normaliser(Courbes):
    n_max = nb_point_to(Courbes[0],200)
    couleurs = ['b','g','r','m']
    for k in range(len(Courbes)//3):
        (Courbes[3*k],Courbes[3*k+1]) = fixer_nbr_point_fonction(Courbes[3*k].tolist(),Courbes[3*k+1].tolist(),n_max,np.min(Courbes[3*k]),200)
    #     plt.plot(Courbes[3*k],Courbes[3*k+1],couleurs[Courbes[3*k+2][0]])
    #     plt.xlabel("Hz")
    #     plt.ylabel("V")
    #     plt.title("FFT")
    # plt.show()


def Creer_model(Courbes = []):
    if(len(Courbes) == 0):
        remplir(Courbes)
        normaliser(Courbes)
    n_max = max([len(Courbes[3*k]) for k in range(len(Courbes)//3)])
    print(n_max)
    LAYERS = [keras.layers.Input(n_max,dtype="float32")]
    for k in range(3):
        LAYERS.append(keras.layers.Dense((64//(2**k)),activation="relu",dtype="float32"))
    LAYERS.append(keras.layers.Dense(len(C[2]),activation=tf.keras.activations.softmax))
    model = tf.keras.Sequential(LAYERS)
    model.summary()
    model.compile(
        optimizer=tf.optimizers.Adam(),
        loss='mse',
        metrics=[tf.keras.metrics.CategoricalAccuracy()])
    history = model.fit(
        np.array([Courbes[3*k+1] for k in range(len(Courbes)//3)]),
        np.array([Courbes[3*k+2] for k in range(len(Courbes)//3)]),
        epochs=10,
        verbose=1,
        validation_split = 0.2)
    # plt.plot(history.history['accuracy'])
    # plt.plot(history.history['val_accuracy'])
    # plt.title('model accuracy')
    # plt.ylabel('accuracy')
    # plt.xlabel('epoch')
    # plt.legend(['train', 'test'], loc='upper left')
    # plt.show()
    # plt.plot(history.history['loss'])
    # plt.plot(history.history['val_loss'])
    # plt.title('model loss')
    # plt.ylabel('loss')
    # plt.xlabel('epoch')
    # plt.legend(['train', 'test'], loc='upper left')
    # plt.show()
    err = 0
    # L_estime = model.predict([Courbes[3*k+1] for k in range(len(Courbes)//3)]).tolist()
    #
    # err = 0
    # for k in range(len(Courbes)//3):
    #     if(k < len(Courbes)//6 and L_estime[k][0]>0.5):
    #         err += 1
    #     if(k>= len(Courbes)//6 and L_estime[k][0]<0.5):
    #         err += 1
    # print(err," erreur, sur ",len(Courbes)//3, " exemples")
    # model.save("mymodel")
    return(err,model,history)


def trouver_model(C = []):
    if(len(C) == 0):
        remplir(C)
        normaliser(C)
    accuracy_max = 0
    m_actuel = None
    h_actuel = None
    k = 0

    while(accuracy_max < 0.8 and k<200):
        print(k)
        k+=1
        (e,m,h) = Creer_model(C)
        if(h.history["categorical_accuracy"][9]>accuracy_max):
            accuracy_max = h.history["categorical_accuracy"][9]
            m_actuel = m
            h_actuel = h
    return(accuracy_max,m_actuel,h_actuel)





def analyse(lien):
    model = keras.models.load_model(Lien_dossier + "/Test_FINAL")
    n_inputs = model.input.shape[1]
    n_outputs = model.output.shape[1]
    with open(lien, newline='') as f:
        reader = csv.reader(f)
        data = [tuple(row) for row in reader]
    X,Y=[],[]

    for i in range(2,len(data)):
        (x,y)=data[i][-2:]
        x=float(x)
        y=float(y)
        X.append(x)
        Y.append(y)
    L = []
    for k in range(50):
        X2 = X.copy()
        Y2 = Y.copy()
        X2,Y2 = random_tranche(len(X2)//2,X2,Y2)
        X2,Y2=np.array(X2),np.array(Y2)
        Y2=Y2-np.mean(Y2)
        SAMPLE_RATE= np.mean([X2[k+1]-X2[k] for k in range(len(X2)-1)])
        DURATION= X2[len(X2)-1]-X2[0]
        N = len(X2)
        yf = fft(Y2)
        yf = np.abs(np.real(yf))
        xf = fftfreq(N, SAMPLE_RATE)
        xf,yf = xf[0:len(xf)//30],yf[0:len(yf)//30]
        xf,yf = fixer_nbr_point_fonction(xf.tolist(),yf.tolist(),n_inputs,0,200)
        L.append(yf)
    plt.plot(xf,yf,linewidth=0.4)
    plt.savefig("new.png")
    #plt.show()
    predict = model.predict(L)
    resultat = [0] * n_outputs
    for k in range(50):
        for n in range(n_outputs):
            resultat[n] += predict[k][n] / 50
    print("Cet fft appartient à un ventilateur est", catégorie[resultat.index(max(resultat))])
    return(resultat)


def test():
    erreur = 0
    succes = 0
    for nom in([("test23_",[0]),("test24_",[1]),("test25_",[1]),("test29_",[2]),("test31_",[2]),("test33_",[2]),("test35_",[2]),("test39_",[2]),("test37_",[2])]):
        for k in range(1,6):
            RESULTAT = analyse(Lien_dossier + "/" + nom[0] + str(k) + ".csv")
            index = RESULTAT.index(max(RESULTAT))
            if(index != nom[1][0]):
                print("Erreur sur", nom[0], k )
                print(RESULTAT)
                erreur += 1
            else:
                succes += 1
    print(erreur, " erreurs | " , succes , " succes |", str(erreur/(erreur+succes)))
