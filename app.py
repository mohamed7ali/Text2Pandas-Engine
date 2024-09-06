# Import packages.
import streamlit as st
import os
import google.generativeai as genai
from htmlTemplates import css, bot_template, user_template
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

# Load the environment variables from a .env file into the environment.
load_dotenv()
# Configure the Google Generative AI module with the API key retrieved from the environment variables.
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])



# Extract text from a CSV.
def get_csv_text(csv_docs):
    df = pd.read_csv(csv_docs)
    return df



# manages the conversation flow and simulate a conversation between the user and the system.
def handle_userinput(user_question, response):
    # Load the dataframe
    df = st.session_state.df
    # Add the question to the list
    st.session_state.conversation.append({'question': user_question})

    # Add the response to the list if it's punt without excution of the code
    if "I don't have the context to answer this" in response:
        st.session_state.conversation.append({'answer': response})
    
    # Add the response to the list and the code excution of the code in the response
    else:    
        final_response = f"The pandas command to achive this is the following:\n {response} \n \
            \n and the result will be the following: \n {eval(response)}"
        st.session_state.conversation.append({'answer': final_response})

    # Display the questions and answers like a conversation
    for i, message in enumerate(st.session_state.conversation):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message["question"]), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message["answer"]), unsafe_allow_html=True)




def main():
    # Set up the GUI.
    st.set_page_config("Chat Pandas")
    st.header("Chat with your data using Gemini")
    st.write(css, unsafe_allow_html=True)


    # Intialize conversation to store questions and responses.
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Intialize dataframe to store the data uploaded by the user.
    if "df" not in st.session_state:
        st.session_state.df = None



    # Take user's question or query.
    input = st.chat_input("ask me about your data!")
    # Handle it if there is any
    if input:
        
        model = genai.GenerativeModel('gemini-1.5-pro')

        # Pass the prompt with the parameters to the model to get a response
        response = model.generate_content(f"The user will ask you something about the dataframe that has the\
                        the following columns {str(st.session_state.df.columns)} your job is to provide\
                        the code that will solve the user problem only don't explain just the code \
                        and if the question is not relevent to the data or the context say\
                        'I don't have the context to answer this' for example if the user question is:\
                        'What is the maximum value for counter_2 for all of the cells?' \
                        your answer should be like this: 'df.groupby('cell_no')['counter_2'].max()' \
                        now the question is: {input}\
                        ")
        

        # Pass the question and the answer after refinement to get just the code
        handle_userinput(input, response.text.replace("`", "").replace("python", "").strip())
    





    # Create the sidebar components and content.
    with st.sidebar:
        st.title("Menu:")
        # Get user's file.
        doc = st.file_uploader("Upload your data file with `.csv` extension and Click on the `Submit & Process` Button", accept_multiple_files=False)
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):
                
                # Check documents type or extension.
                file_extension = os.path.splitext(doc.name)[1].lower()

                if file_extension == ".csv":
                    
                    st.session_state.df = get_csv_text(doc)
                    # Success message at the end :)
                    st.success("Done")
                else:
                    st.warning("Please upload .csv files only")

                    
                
                



if __name__ == "__main__":
    main()
