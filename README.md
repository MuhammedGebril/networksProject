# networksProject
in this project we simulate the reliable TCP connection using unreliable UDP connection with the addition of some manual reliability.
the project consists of 4 files:
1. client file.
2. server file.
3. **horu.py** *(http over reliable UDP)* : this file contains the logic of http class like GET and POST implementation , Parser of http request and constructor of the response . creates a packet to be converted to a segment to be transmitted.
4. **tcp.py**: this file contains the logic of reliable data transfer . the class operates on a http object and adds the reliable data transfer logic to construct the segment to be sent.  
