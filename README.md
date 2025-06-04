# AI Bookclub

*This project emulates a bookclub using a single, linear chat populated by several AI personalities.*

Be warned, running this project can get expensive quickly as the chat requires a lot of input context tokens.

### Installation

1. clone it
2. add secrets

```
echo "OPENAI_API_KEY=my-key-here" > secrets.sh
source secrets.sh
```

3. Install dependencies

```
$ pip install -r requirements.txt
```

4. You're off!

```
$ python3 bookclub.py
```


### Configuring

Modify either the `agents/*.txt` files to change the personality of some agents or add new files with a `<name>.txt` to that same directory to include them in the conversation.

