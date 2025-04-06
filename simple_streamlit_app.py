import streamlit as st

st.set_page_config(page_title="Simple Test App", layout="wide")

def main():
    st.title("Simple Test App")
    st.write("This is a test to see if Streamlit works correctly.")
    
    if st.button("Click Me"):
        st.success("Button clicked!")

if __name__ == "__main__":
    main()