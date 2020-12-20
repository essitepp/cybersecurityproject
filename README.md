# Cyber Security Project

## Report

For testing, the app has the following users:

- username: testuser1, password: testpassword1

- username: testuser2, password: testpassword2



**Flaw 1: SQL injection**

When creating a new note, unsanitized user inputs are inserted into the SQL query in the view *add_note*. This makes it possible for the user to input a string that alters the function of the query and access data from the database that should not be available. The contents of the title and input fields are rendered on the page, so the user can see the accessed data by inserting it into either of these fields.

For example, by inputting the string *', (select password from auth_user where id=1))--* into the title field, the user can obtain the password hash of the user whose id is specified in the string.

Injection can be prevented by making sure all user inputs are sanitized when using them as parts of an SQL query. An easy way to do this is to use Django models to handle data instead of direct queries into the database.

The fixed *add_note* view is:

    @login_required
    def add_note(request):
      if request.method == 'POST':
        title = request.POST.get('note_title')
        text = request.POST.get('note_text')
        note = Note.objects.create(note_title=title, note_text=text, owner=request.user)
      return redirect('/')
  


**Flaw 2: Cross-site scripting**

While switching to using Django models for creating new notes prevents SQL injections, 
it is still possible for the user to input malicious content.

The application still renders data inputted by the user on the page without checking it.
The user can therefore input HTML that will alter the page. By using the `<script>` tags 
it is possible to execute malicious JavaScript code.

This can then be used to, for example, steal authentication cookies. 
By inputting the string *<script>alert(document.cookie);</script>* into either the title or content field, 
we get an alert window showing the cookies. The script could then be altered so that instead of showing an alert,
it sends the cookies to the attacker.

This type of attack is possible because the variables `note.note_title` and `note.note_content` 
are marked as safe in the note list in *index.html*, meaning they are rendered without escaping. 
When the template tag `safe` is removed, the HTML is escaped, and the contents are rendered as a string, 
preventing the execution of scripts. 

Thus, the safe way to list the notes is:

    {% if notes %}
    <ul>
      {% for note in notes %}
      <li>
        <form action="delete/{{ note.id }}/" method="POST">
          <b>{{ note.note_title }}:</b> {{ note.note_text }}
          <input type="submit" value="Delete">
        </form>
      </li>
      {% endfor %}
    </ul>
    {% else %}
    <p>No notes added yet</p>
    {% endif %}



**Flaw 3: Broken access control**

When deleting a note, the application uses the view *delete_note*, 
which does not check that the user is logged in or that the user owns the note they are trying to delete. 
This means anyone can delete any note by simply making a POST request to the address *delete/[note_id]/*.

Checking that the user is logged in can be done by using Django’s `login_required` decorator. 
To check that the user owns the note, we can include the check `note.owner == request.user` before deleting the note.

The fixed *delete_note* view becomes:

    @login_required
    @csrf_exempt
    def delete_note(request, note_id):
      if request.method == 'POST':
        note = Note.objects.get(pk=note_id)
        if note.owner == request.user:
          note.delete()
      return redirect('/')



**Flaw 4: Broken authentication**

Deleting a note does not use a csrf-token, which makes it possible to perform a cross site request forgery attack. 
If a user is logged in, another site they access can send the note application a request to delete a note. 
Because the user is authenticated into the app, the browser can include an authentication token with the request.

Cross site request forgeries can be avoided by including a csrf-token into all forms in the application. 
When a form is sent, the server checks that the form data it received includes the correct token. 
This ensures that the request originated from the application and not from a different site.

The fixed *delete_note* view is now:

      @login_required
      def delete_note(request, note_id):
        if request.method == 'POST':
          note = Note.objects.get(pk=note_id)
          if note.owner == request.user:
            note.delete()
        return redirect('/')
 
and the fixed note deletion form:

        <form action="delete/{{ note.id }}/" method="POST">
          {% csrf_token %}
          <b>{{ note.note_title }}:</b> {{ note.note_text }}
          <input type="submit" value="Delete">
        </form>



**Flaw 5: Security misconfiguration**

The application’s database includes an administrator account that was used for testing during development 
and was meant to be removed. The account’s username is *admin* and password is *password*, 
so it is easy for anyone to guess these and log in as an administrator, 
allowing them to access and modify all users and notes.

To avoid this problem, we must make sure that any testing data is not included with the app 
when it goes into production. Therefore, a separate testing database should be used during development. 
It is also important to make sure common or short passwords are not accepted by the system.

