import streamlit as st
import streamlit.components.v1 as components

def show():
    st.markdown("""
        <h2 id="crm-header" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background-color: #0f1b2b;
            color: white;
            font-weight: 700;
            padding: 15px 0;
            text-align: center;
            z-index: 999;
            box-shadow: 0 2px 5px rgba(0,0,0,0.4);
            transition: top 0.4s ease;">
            📊 Dashboard Tổng quan CRM
        </h2>

        <div style="margin-top:90px;"></div>
    """, unsafe_allow_html=True)

    # iframe Power BI full màn hình
    components.html(
        """
        <html>
        <head>
        <style>
            html, body {
                margin: 0;
                padding: 0;
                overflow: hidden;
                height: 100%;
                background-color: #0f1b2b;
            }
            iframe {
                width: 100vw;
                height: 100vh;
                border: none;
            }
        </style>
        </head>
        <body>
            <iframe title="modun_crm_customer1"
                src="https://app.powerbi.com/view?r=eyJrIjoiMzVkOGY2MjEtNjlhMC00MWEyLTk2ZWYtYWZjYmUyODBiYjZiIiwidCI6IjZhYzJhZDA2LTY5MmMtNDY2My1iN2FmLWE5ZmYyYTg2NmQwYyIsImMiOjEwfQ%3D%3D&pageName=25d8ff63bedf72b5ea42"
                allowFullScreen="true"></iframe>

            <script>
                let lastScrollTop = 0;
                window.addEventListener("scroll", function(){
                    let header = window.parent.document.getElementById("crm-header");
                    let st = window.pageYOffset || document.documentElement.scrollTop;
                    if (st > lastScrollTop){
                        header.style.top = "-80px";   // Ẩn header khi cuộn xuống
                    } else {
                        header.style.top = "0";       // Hiện lại khi cuộn lên
                    }
                    lastScrollTop = st <= 0 ? 0 : st;
                }, false);
            </script>
        </body>
        </html>
        """,
        height=800,
        scrolling=True,
    )
