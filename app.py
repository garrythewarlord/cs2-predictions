import customtkinter
import pandas as pd
import predict as model
import pyperclip
import data_parser as parser

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.resizable(width=False, height=False)
app.geometry("800x225")
app.title('predictor')

my_font = customtkinter.CTkFont(size=10)

def Predict_Button():

    textbox_predict.delete('0.0', 'end')

    import pandas as pd
    data = pd.read_csv('predict_upcoming.csv', encoding='unicode_escape')

    data['venue_code'] = data['event'].astype('category').cat.codes
    data['ranking_opponent_code'] = data['opponent-ranking']


    upcoming_matches = parser.get_upcoming_matches()


    dist = model.dist
    predictions = model.Predict(dist, False)

    accuracy, precision, rf, predictors = predictions['accuracy'], predictions['precision'], predictions['rf'], predictions['predictors']

    accuracy_label.configure(text='Accuracy: {}%'.format(round(accuracy * 100, 2)))
    precision_label.configure(text='Precision: {}%'.format(round(precision * 100, 2)))


    for e in upcoming_matches:
        result = model.Single_Predict(rf, data.iloc[e], predictors)

        if ' ' in result[1] or ' ' in result[2]:
            team = result[1].replace(' ', '-')
            opponent = result[2].replace(' ', '-')
        else:
            team = result[1]
            opponent = result[2]

        textbox_predict.insert('{}.0'.format(e+1), "{} {} {} {} {}\n".format(result[0], team, opponent, upcoming_matches[e]['team_odds'], result[3]))

def Copy_Matches():
    text = textbox_predict.get('1.0', 'end-1c')
    pyperclip.copy(text)



def Show_Upcoming_Button():

    textbox_predict.delete('0.0', 'end')

    upcoming_matches = parser.get_upcoming_matches()
    for match in upcoming_matches:
        textbox_predict.insert('{}.0'.format(match), '{} | {} vs. {}\n'.format('Today', upcoming_matches[match]['team'], upcoming_matches[match]['opponent']))

    #save
    parser.download_upcoming_matches()





# Text boxes
textbox_predict = customtkinter.CTkTextbox(app, width=600, height=160)
textbox_predict.configure(state='normal', font=my_font)
textbox_predict.place(x=180, y=20)

accuracy_label = customtkinter.CTkLabel(app, text="")
accuracy_label.place(x=20, y=100)
precision_label = customtkinter.CTkLabel(app, text="")
precision_label.place(x=20, y=140)


textbox_accuracy = customtkinter.CTkTextbox(app, width=600, height=160)
textbox_accuracy.configure(state='normal')
textbox_accuracy.place(x=180, y=240)




# Buttons
button_predict = customtkinter.CTkButton(master=app, fg_color='gray25', hover_color='goldenrod4', text="Predict", command=Predict_Button)
button_predict.place(x=20, y=20)

button_show_upcoming = customtkinter.CTkButton(master=app, fg_color='gray25', text="Save Upcoming", command=Show_Upcoming_Button)
button_show_upcoming.place(x=20, y=60)

button_copy_predictions = customtkinter.CTkButton(master=app, height=20, width=50, fg_color='gray25', text="Copy", command=Copy_Matches)
button_copy_predictions.place(x=180, y=185)



app.mainloop()