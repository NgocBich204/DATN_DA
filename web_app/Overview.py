import streamlit as st
import streamlit.components.v1 as components

def show():
  

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
            <iframe title="dashboard_crm" src="https://app.powerbi.com/view?r=eyJrIjoiZTkyNjBjMmItNTczZi00NTlhLWE2YzAtNzlhYzU2ZmI3OGY4IiwidCI6IjZhYzJhZDA2LTY5MmMtNDY2My1iN2FmLWE5ZmYyYTg2NmQwYyIsImMiOjEwfQ%3D%3D&pageName=25d8ff63bedf72b5ea42" frameborder="0" allowFullScreen="true"></iframe>
                

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
