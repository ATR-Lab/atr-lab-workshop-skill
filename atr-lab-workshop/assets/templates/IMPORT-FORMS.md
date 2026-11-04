# Create the Google Forms

Google Forms has no "import from file" button. `create-forms.gs` is the import: a Google Apps Script that builds
every form described in the `*.form.json` files in this folder, in your own Google Drive. It takes about two
minutes.

1. Sign in to the Google account that should own the forms (a Kent State Google account keeps them in the
   university's Workspace).
2. Open <https://script.google.com> and choose **New project**.
3. Delete the sample code in `Code.gs`, then paste in the whole of `create-forms.gs`. Save (Ctrl+S or Cmd+S).
4. In the toolbar, choose the function **createAllForms** and press **Run**.
5. Google asks for permission the first time: **Review permissions**, pick your account, **Allow**. A Workspace
   account may show "Google hasn't verified this app" for a script you wrote yourself: **Advanced**, then
   **Go to (project name)**.
6. When the run finishes, open the **Execution log**. Below the line `copy everything below back to the agent`
   there is one line per form with its `edit_url`, `respond_url` and `short_url`.
7. Paste those lines back to the agent (or run
   `python3 scripts/workshop.py set registration.url <respond_url>` and
   `python3 scripts/workshop.py set registration.printed_url <short_url without https://>`).
   The agent rebuilds the flyers, the TV slide and the feedback slide so their QR codes point at the real forms.

## Before you share the links

- Open each form's `edit_url`, read it once and press **Preview** (the eye icon).
- **Settings > Responses**: decide whether respondents must sign in to Google. Requiring sign-in blocks people
  without a Google account; the generated forms ask for an email address instead.
- If the form has a capacity, a trigger closes it after that many responses. Reopen it in **Responses >
  Accepting responses**.
- Responses go to a new Google Sheet named "(form title) (responses)" when the spec asks for one.
- Running the script again creates a second copy of every form. Delete the copies you don't use.

## Changing a form later

Edit it directly in Google Forms, or edit the `.form.json` file, run `workshop.py forms build`, and run the new
script (it makes new forms; the old links keep pointing at the old ones).
