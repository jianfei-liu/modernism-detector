# Modernism Feature Detector

This small app looks for features often linked with **literary modernism**
(roughly 1890–1940): vocabulary, ideas and political ideas. A high score means
the text shares these features. **It does not prove that the text belongs to
the historical Modernist movement**, because writers before and after that
period use these features too.

## Set it up on Windows

1. Install Python 3.11 or newer from [python.org](https://www.python.org/downloads/).
   During setup, tick **Add python.exe to PATH**.
2. In File Explorer, right-click the downloaded zip file and choose **Extract All**.
3. Open the new folder and double-click **Start Modernism App.bat**.
4. If Windows shows a blue **Windows protected your PC** box, click
   **More info**, then **Run anyway**. This is normal for downloaded `.bat` files.
5. The first start takes about 2 minutes while the app sets itself up. Then
   your browser opens at `http://localhost:8501`.
6. To use Kev, paste your key in the sidebar. The start file enables
   **Remember my key on this computer**; tick it if you want the key saved
   outside the app folder, only on this computer.
7. Keep the black window open while you use the app. Close it to stop the app.

To make a desktop shortcut, right-click **Start Modernism App.bat**, choose
**Show more options** → **Send to** → **Desktop (create shortcut)**.

### Advanced: start it by hand

If you prefer to use Command Prompt, open it in the project folder and run:

```text
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Connecting Kev

Kev is an optional AI reading tool. Get a personal key from the
[Kev workshop site](https://yohann-60613--kev-demo.modal.run) by choosing
**Request a key**, then paste the key into the sidebar. The first analysis
after the service has been quiet can take 3–4 minutes while it wakes up.

You can also set the key in Command Prompt before starting Streamlit:

```text
set KEV_DEMO_KEY=kevdemo_your_key_here
streamlit run app.py
```

## Put it online (Streamlit Community Cloud)

1. Create a GitHub repository and upload the project files. Do not upload the
   `venv` folder.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and choose **Create
   app**.
3. Select your repository, branch `main`, and file `app.py`.
4. Leave **Advanced settings** → **Secrets** empty. Each visitor can paste
   their own Kev key. Visitors without a key can still get word-list results.
5. Choose **Deploy**.

Optional: If you put `KEV_DEMO_KEY` in Secrets, the site uses your key for
every visitor and uses your Kev credit.

## Understanding the scores

The word-list scores count vocabulary that appears in lists grouped by theme.
The Vocabulary, Ideas and Political ideology scores are each from 0 to 100.
The Overall score is the average of those three word-list scores.

0 means the listed terms appear about as rarely as in 19th-century novels such
as *Pride and Prejudice* or *Great Expectations*. 100 means they appear as
often as, or more than, in the strongest modernist works tested, such as
*The Waste Land* and *Jacob's Room*. Scores from short texts are less reliable.
Word lists only count words; they cannot tell how a word is used, and a word
may have a different meaning in context.

Kev reads one passage of about 1,500 words. Its AI scores are shown separately
from the word-list scores; the two kinds of scores are not combined.

## Putting it on GitHub (optional)

A repository is an online project folder.

1. Sign in to GitHub as **jianfei-liu** and open [github.com/new](https://github.com/new).
2. Name the repository `modernism-detector`, then click **Create**.
3. Choose **uploading an existing file**.
4. Drag in the unzipped project files. Do not upload the `venv` folder.
5. Click **Commit changes**.

## Running the tests

In Command Prompt, with the project environment active, install the development
packages and run the tests:

```text
pip install -r requirements-dev.txt
pytest -q
```
