# Xenforo-2-threads-parser
Threads parser from xenforo 2

```
usage: xenforo_parser.py [-h] [--url URL] [--sleep SLEEP] [--autoposting]

Process some integers.

optional arguments:
  -h, --help            show this help message and exit
  --url URL, -u URL     link to the forum page
  --sleep SLEEP, -s SLEEP
                        waiting time before logging in to the forum
  --autoposting, -a     automatically create topics on your forum using the REST API
```

The parser automatically downloads all threads on the same page in the forum. When using `--autoposting`, the parser will automatically create threads on your forum. 

At the moment, there is no support for attachments!

- [x] Automatically create threads using the REST API.
- [x] Parsing threads from the page.
- [ ] Selecting the parser mode: selenium/requests.
- [ ] Ability to log in to your account before parsing.
- [ ] Parsing all threads in a section or selecting the number of pages.
- [ ] Automatic creation of threads with attachment support.
