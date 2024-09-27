Extraction of Fields
====================

The problem
-----------

*This is the meat of the project. This is the most important part!*

So basically the idea is, How do we identify and extract each question and it's
related answer field (e.g. Text box, Checkbox, Radio buttons, Drop downs, etc)?

The challenge
-------------

The most difficult challenge in identifying individual parts of the web forms is that
each stupid HR website has its own framework/structure to build the form. Since their
content is highly dynamic, no two HR website use the same pattern. Especially, I've seen weak to none
adherence to the standard HTML form structure.

The solutions
-------------

This is a tough nut to crack!

Since starting the project, up until now, I've though about and researched different
solutions:

1. Rule Based Extraction:

This is basically the way to tell selenium what to extract from a form using IF
... THENs. This method relies on pseudo-unique features of each forms. The
extensibility of this method is extremely limited.

I have already made an example of such approach in my code.

2. Computer Vision:

Using image recognition techniques to find the elements of a web page.

This approach needs you to transmit the page data as picture format. Obviously
computer vision looks like the closest approach to *Natural* human perception of forms.

However, there are some pro

3. Language Models:
    I. Open AI and other LLMs
        **Phind** is promising! 
    II. Extractnet
        See: `Their guthub page <https://github.com/currentslab/extractnet>`_

