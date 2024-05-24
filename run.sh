#!/bin/sh
clear
cd docscope
find . -name '*.py' | sed 's/.*/"&"/' | xargs  wc -l
cd ..

# run your streamlit app
#source venv/bin/activate
#python -m streamlit run docscope/app.py
streamlit run docscope/app.py
#nohup streamlit run docscope/app.py  

# testing
#cd docscope
#python3 -m pytest -v