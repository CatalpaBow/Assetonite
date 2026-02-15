# Setup
1. Clone respository `gh repo clone CatalpaBow/Assetonite`
2. Create virtual enviroment `uv sync` 
# How to use
Haven't written yet.


# Structure
**Sender:** Serializes and sends messages

**Message:** Generates messages based on the message source

**MessageSource:** Produces and provides the data required to generate messages from raw data

**RawData:** Retrieves raw data such as ini files or SharedMemory

**message_server:** Implements the entire messaging process using Reactive Programming