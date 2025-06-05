# Golem

A simple tool to download/extract LaTeX files and images from [RevisionVillage](https://www.revisionvillage.com). It requires an account with a RV Gold subscription to extract the content supplied in the questionbanks.

### Setup
This tool requires the `pycryptodome` and `requests` packages to be installed. Use UV to sync your environment in order to run it:
```console
uv sync 
```
Afterwards, use the [Cookie Editor](https://cookie-editor.com/) extension to extract your cookies from the Revision Village website. Simply navigate to it, and click on the "Export" icon in the extension's toolbar, saving it as "cookies.json" in the root directory of the repository.

Do note that this requires that you are authenticated on RV.

### Usage
Simply run the `main.py` file.
```
uv run main.py
```
You will then be prompted to input your subject URL. In the case of IB Mathematics AA HL, this is "ib-math/analysis-and-approaches-hl", as can be seen from the URL for it: https://www.revisionvillage.com/ib-math/analysis-and-approaches-hl/

Golem will now extract all questions categorized into topics and subtopics in the "questions" subdirectory of the repo.

### Technical Details
RV uses NextJS to handle their site navigation, which provides JSON files containing data on the question contents and mark scheme. The LaTeX markup files contained are encrypted using AES CBC, which Golem decrypts by creating an IV (Initialization Vector), salt as well as a key derived from the user's account ID.

Every "request" (site navigation) generates a "Ephemeral Key" (request ID) which is valid only for the contents of the file at that moment. By combining it with the "LastAuthUser" (account ID) cookie, you can create an initial key with a content similar to "<RequestID>-<AccountID>-_content". In this case, the "_content" suffix determines which field that can be decrypted.

The data is additionally encoded in Base64, which is decoded in the final output.

The LaTeX format that RV uses is non-standard and can't be used by a LaTeX compiler directly, so the text is processed afterwards. This includes:
- Removing redundant paranthesis
- Replacing macros such as ":marks" with their representation
- Replacing italic and bold text with their latex text counterparts.
- Replacing RV's custom image macro with one powered by `svg` and `graphix`
- Converting indentation to tabs
+ more.

Do note that this post processing may result in an inaccurate representation of the question/mark scheme contents. Further work will be done to improve it.

### Legal Disclaimer
This tool is provided solely for educational and personal use purposes. For information on what you can and cannot do with this tool, please refer to Revision Village's [Terms of Service](https://www.revisionvillage.com/terms-and-condition)

By using this tool, you acknowledge Revision Village's right to prevent or restrict access to content hosted on their website. Any and all damages that may occur to your account, access rights, or other consequences resulting from the use of this tool are solely your responsibility.

This tool is not affiliated with or endorsed by Revision Village.
