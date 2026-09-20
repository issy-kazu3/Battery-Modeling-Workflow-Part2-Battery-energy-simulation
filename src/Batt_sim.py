import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #グラフをdialogに埋め込むためのｍの
import tkinter as tk        #ダイアログボックスでの入力パラメータ入力のため
from tkinter import ttk     #表を作るためのもの

import pandas as pd
#import numpy as np
from bat_pack_cond_loader import load_conditions 
from load_drive_condition import load_drive_condition
from ir_map_load import load_ir_map
from interpolate_cell import map_const
from bat_sequential_calc import bat_disc_calc

def create_result_plot(parent,df_results):  #グラフの作成
    fig,ax1=plt.subplots(figsize=(10,5))

    time=df_results["time"]

    #------------------
    #左軸：power
    #------------------
    ax1.plot(
        time,
        df_results["power"],
        label="power command",
        color="blue",
        linestyle="--"
    )
    ax1.plot(
        time,
        df_results["output"],
        label="output",
        color="orange",
        linestyle="-"
    )

    ax1.set_xlabel("time [sec]")
    ax1.set_ylabel("Power [W]")
    ax1.grid(True)

    #------------------
    #右軸
    #------------------
    ax2=ax1.twinx()

    ax2.plot(
        time,
        df_results["current"],
        label="current",
        color="purple",
        linestyle="--"
    )

    ax2.plot(
        time,
        df_results["voltage"],
        label="voltage",
        color="red",
        linestyle="-"
    )

    ax2.plot(
        time,
        df_results["soc"],
        label="soc",
        color="green",
        linestyle="-"
    )

    ax2.set_ylabel("A / V / Soc")

    #凡例をまとめる
    lines1,labels1=ax1.get_legend_handles_labels()
    lines2,labels2=ax2.get_legend_handles_labels()

    ax1.legend(
        lines1+lines2,
        labels1+labels2,
        loc="upper left",
        bbox_to_anchor=(1.06, 1.0)
    )
    fig.subplots_adjust(right=0.78)

    ax1.set_ylim(-80000,100000)
    ax2.set_ylim(-400*(max(df_results["current"].max(),df_results["voltage"].max())//500+1),500*(max(df_results["current"].max(),df_results["voltage"].max())//500+1))

    fig.tight_layout()

    #Tkinterに埋め込む
    canvas=FigureCanvasTkAgg(
        fig,
        master=parent
    )

    canvas.draw()

    canvas.get_tk_widget().pack(
        fill=tk.BOTH,
        expand=True
    )

    return fig,canvas   #figがグラフで、canvasがダイアログの生地部分か

def create_result_table(parent,df_results,df_conclusion):
    frame=ttk.LabelFrame(
        parent,
        text="Simulato result"
    )

    frame.pack(
        fill=tk.X,
        padx=10,
        pady=10
    )

    items=[
        ("cell_capa Ah",f"{df_conclusion['cell capa'].iloc[0]:.2f} Ah"),
        ("cell_max_V",f"{df_conclusion['max v'].iloc[0]:.1f} V"),
        ("cell_min_V",f"{df_conclusion['min v'].iloc[0]:.1f} V"),
        ("Stat_soc",f"{df_conclusion['start soc'].iloc[0]:.1f} %"),
        ("finished_soc",f"{df_conclusion['finished soc'].iloc[0]:.1f} %"),
        ("max_current_limit",f"{df_conclusion['max current'].iloc[0]:.1f} A"),
        ("max_cell_chg_current_lmt",f"{df_conclusion['max charge cell current'].iloc[0]:.1f} A"),
        ("max_system_v_lmt",f"{df_conclusion['max sys v'].iloc[0]:.1f} V"),
        ("min_system_v_lmt",f"{df_conclusion['min sys v'].iloc[0]:.1f} V"),
        ("n_serial",f"{df_conclusion['n-seri'].iloc[0]}"),
        ("n_parallel",f"{df_conclusion['n-para'].iloc[0]}"),
        ("pack wt",f"{df_conclusion['pack weight kg'].iloc[0]:.1f} kg"),
        ("DOD",f"{df_conclusion['DOD'].iloc[0]:.1f} %"),
        ("max_cell_v",f"{df_results['voltage'].max()/df_conclusion['n-seri'].iloc[0]:.1f} V"),
        ("min_cell_v",f"{df_results['voltage'].min()/df_conclusion['n-seri'].iloc[0]:.1f} V"),
        ("Total loss",f"{df_conclusion['total loss wh'].iloc[0]:.1f} Wh"),
        ("result",df_conclusion['result'].iloc[0]),
    ]

    for i,(name,value) in enumerate(items):
        row=i//3
        col=(i%3)*2

        if i < 9:
            result_color="black"
        elif i< 16:
            result_color="blue"
        else:
            if value=="Passed":
                result_color="green"
            else:
                result_color="red"

        tk.Label(
            frame,
            text=name,
            fg=result_color,
            font=("Arial",14)

        ).grid(
            row=row,
            column=col,
            padx=10,
            pady=5,
            sticky="w"
        )

        tk.Label(
            frame,
            text=value,
            fg=result_color,
            font=("Arial",14)
        ).grid(
            row=row,
            column=col+1,
            padx=10,
            pady=5,
            sticky="w"
        )
    return frame

def show_result(df_results,df_conclusion):

    #root=tk.Tk()
    window=tk.Tk()
    window.title("Bat simulator result")

    window.geometry("1200x900")

    #-----------------
    #タイトル
    #-----------------
    title=ttk.Label(
        window,
        text="Bat simulator result",
        font=("Arial",16,"bold")
    )

    title.pack(
        pady=10
    )

    #-----------------
    #グラフ領域
    #-----------------
    graph_frame=ttk.Frame(window)

    graph_frame.pack(
        fill=tk.BOTH,
        expand=True,
        padx=10,
        pady=5
    )

    create_result_plot(
        graph_frame,
        df_results
    )

    #--------------
    #結果表
    #--------------
    create_result_table(
        window,
        df_results,
        df_conclusion
    )

    window.wait_window()





#csv_path=r"C:\Users\kazi3\Documents\my_program\Github\python_battery\battery"
csv_path=r"C:\Users\kazi3\Documents\my_program\Github\python_battery\battery\apply_dialog_box"
file_drive=r"drive_condition.csv"
file_pack=r"bat_pack_condition.csv"
file_map=r"IR_MAP.csv"

def get_conditions(dic_config):     #ここではからなず引数に使う辞書dic_configを入れねばならない

    confirmed=False #confirmedはここで作った関数ローカルの変数 Falseだと、そのままwindowが閉じられたことを呼び出し側に知らせる

    def start_simulation():

        nonlocal confirmed  #ローカル変数でない。上の変数を使うという宣言

        dic_config["cell capa(Ah)"]=dic_config["cell capa(Ah)"]
        dic_config["wt g"]=dic_config["wt g"]
        dic_config["n-seri"]=int(entry_seri.get())
        dic_config["n-para"]=int(entry_para.get())
        dic_config["start soc"]=float(entry_soc.get())
        dic_config["max current"]=float(entry_current.get())
        dic_config["max charge cell cur"]=float(entry_charge_current.get())
        dic_config["max sys v"]=float(entry_max_sys_v.get())
        dic_config["min sys v"]=float(entry_min_sys_v.get())
        dic_config["max v"]=float(entry_max_cell_v.get())
        dic_config["min v"]=float(entry_min_cell_v.get())

        confirmed=True  #正しく終了した場合には、False->Trueに変更する！
        window.destroy()

    def cancel():    #windowがそのまま閉じられた場合の関数
        window.destroy()    #そのままwindowを消滅させている。confirmedはFalseのまま

   #conditions={}

    window=tk.Tk()
    window.title("Battery pack condition")
    window.geometry("300x300") #windowの幅を指定

    #xボタンを押したときもcancel()を実行
    window.protocol("WM_DELETE_WINDOW",cancel)  #mainloop()の前に指定しておく　windowが消されたらcancel()

    tk.Label(window,text="cell capa(Ah)").grid(row=0,column=0)
    tk.Label(window,text=str(dic_config["cell capa(Ah)"])).grid(row=0,column=1)
    tk.Label(window,text="cell wt g").grid(row=1,column=0)
    tk.Label(window,text=str(dic_config["wt g"])).grid(row=1,column=1)
    tk.Label(window,text="n-seri").grid(row=2,column=0)
    entry_seri=tk.Entry(window,justify="center")            #tk.Entryはテキストボックス
    entry_seri.insert(0,str(int(dic_config["n-seri"])))
    entry_seri.grid(row=2,column=1)
    tk.Label(window,text="n-para").grid(row=3,column=0)
    entry_para=tk.Entry(window,justify="center")
    entry_para.insert(0,str(int(dic_config["n-para"])))
    entry_para.grid(row=3,column=1)
    tk.Label(window,text="start soc").grid(row=4,column=0)
    entry_soc=tk.Entry(window,justify="center")
    entry_soc.insert(0,str(dic_config["start soc"]))
    entry_soc.grid(row=4,column=1)
    tk.Label(window,text="system max current A").grid(row=5,column=0)
    entry_current=tk.Entry(window,justify="center")
    entry_current.insert(0,str(dic_config["max current"]))
    entry_current.grid(row=5,column=1)
    tk.Label(window,text="cell max charge current A").grid(row=6,column=0)
    entry_charge_current=tk.Entry(window,justify="center")
    entry_charge_current.insert(0,str(dic_config["max charge cell cur"]))
    entry_charge_current.grid(row=6,column=1)
    tk.Label(window,text="system max voltage V").grid(row=7,column=0)
    entry_max_sys_v=tk.Entry(window,justify="center")
    entry_max_sys_v.insert(0,str(dic_config["max sys v"]))
    entry_max_sys_v.grid(row=7,column=1)
    tk.Label(window,text="system min voltage V").grid(row=8,column=0)
    entry_min_sys_v=tk.Entry(window,justify="center")
    entry_min_sys_v.insert(0,str(dic_config["min sys v"]))
    entry_min_sys_v.grid(row=8,column=1)
    tk.Label(window,text="cell max lmt V").grid(row=9,column=0)
    entry_max_cell_v=tk.Entry(window,justify="center")
    entry_max_cell_v.insert(0,str(dic_config["max v"]))
    entry_max_cell_v.grid(row=9,column=1)
    tk.Label(window,text="cell min lmt V").grid(row=10,column=0)
    entry_min_cell_v=tk.Entry(window,justify="center")
    entry_min_cell_v.insert(0,str(dic_config["min v"]))
    entry_min_cell_v.grid(row=10,column=1)

    tk.Button(
        window,
        text="start simulation",
        command=start_simulation
    ).grid(row=11,column=0,columnspan=2,pady=(20,5))

    window.mainloop()

    if not confirmed:   #キャンセルの場合
        return None

    return dic_config

#conditions=get_conditions()

#print(conditions)

#ここからがメインの処理--------------------------------------

input_file=csv_path+"\\"+file_map
temp,ocv,df_map=load_ir_map(input_file)     #temp温度 socはbunpy配列 df_mapはセルの定数のsoc&charge/discharge map

input_file=csv_path+"\\"+file_drive
drive_cond=load_drive_condition(input_file) #drive_condはnumpy配列

input_file=csv_path+"\\"+file_pack
dic_config=load_conditions(input_file)      #dic_configはパック構成の辞書  ちなみに辞書を多数個束ねたものがリストである  リストからある辞書を取り出すにはresult[i-1] ある辞書のある項目はresult[i-1]["soc"]などの表現となる

dic_config=get_conditions(dic_config)
if dic_config==None:
    dic_config=load_conditions(input_file)

print(dic_config)



soc=dic_config["start soc"]
Vp=0    #batの寄生容量の電圧も共通変数をしてもつ
results=[]  #dataの入れものとしての空の辞書
conclusion=[]

map_data=map_const(ocv,df_map)          #これから使うセルのマップ特性をmap_dataという辞書に入れる

for i in range(len(drive_cond)-1):   #drive_condの長さは、時間と電力の組み合わせの数である。  ここでは、i番目の時間とi+1番目の時間の間で、計算を行う
    t0=drive_cond[i][0]
    t1=drive_cond[i+1][0]
    pw1=drive_cond[i+1][1]

    temp,soc,current,voltage,warning,Wloss,Vp=bat_disc_calc(temp,map_data,dic_config,t0,soc,t1,pw1,Vp)
    results.append({
        "time":t1,
        "power":pw1,
        "soc":soc,
        "current":current,
        "voltage":voltage,
        "output":current*voltage,
        "loss":Wloss,
        "temp":temp,
        "warning":warning,
    })
    if warning!="":
        print("fault at time=",t1,"sec, warning=",warning)
    if (warning=="max voltage limit")or (warning=="min voltage limit"):
        break  #電圧が上限下限を超えたら、そこで計算を打ち切る
df_results=pd.DataFrame(results)
df_results.to_csv(csv_path+"\\bat_sim_result.csv",index=False)

fault = df_results[df_results["warning"] != ""]
if fault.empty:
    first_fault = "Passed"
else:
    first_fault = fault.iloc[0]["warning"]

conclusion.append({
    "cell capa":dic_config["cell capa(Ah)"],
    "max v":dic_config["max v"],
    "min v":dic_config["min v"],
    "start soc":dic_config["start soc"],
    "finished soc":soc,
    "max current":dic_config["max current"],
    "max charge cell current":dic_config["max charge cell cur"],
    "max sys v":dic_config["max sys v"],
    "min sys v":dic_config["min sys v"],
    "n-seri":dic_config["n-seri"],
    "n-para":dic_config["n-para"],
    "pack weight kg":dic_config["wt g"]*dic_config["n-seri"]*dic_config["n-para"]/1000,
    "DOD":df_results["soc"].max() - df_results["soc"].min(),
    "total loss wh":df_results["loss"].sum()/3600,
    "result": first_fault,
    })

df_conclusion=pd.DataFrame(conclusion)
df_conclusion.to_csv(csv_path+"\\bat_sim_conclusion.csv",index=False)   

show_result(df_results,df_conclusion)