#! /usr/bin/env python

import sys
from pprint import pprint
from pathlib import Path
import re
import json
import time

config_json_file = Path(f'scratch/_email/blog_email_config.json')
with open(f'{config_json_file}', 'r') as f:
    config = json.load(f)

work_dir = Path(config['work_dir'])

opt_dict = {
    'verbose_mode':         False,
    'live_mail':            False,  # Set to True to mail to live blog -f
    'test_mail':            True,   # Set to True to mail to test blog -a
    'id_specified':         False,
    'recipients':           [config['blog_mail_test']],
    'leave_as_draft':        False,
    'specify_list_of_rcps': [],
}
blog_id = None

if '-v' in sys.argv:
    opt_dict['verbose_mode'] = True

if '-d' in sys.argv:
    opt_dict['leave_as_draft'] = True

if '-f' in sys.argv:
    opt_dict['live_mail'] = True
    opt_dict['recipients'] = [config['blog_mail_live']]     # send to LIVE blog
    blog_id = config['FOODLAB_BLOD_ID']

if '-e' in sys.argv:
    opt_dict['live_mail'] = True
    opt_dict['recipients'] = [config['blog_mail_email']]    # send to EMAIL

if '-a' in sys.argv:
    opt_dict['live_mail'] = True                            # send to TEST blog
    blog_id = config['AUTO_TEST_BLOG_ID']

if '-i' in sys.argv:
    start_of_specify_list = sys.argv.index('-i') + 1
    pre_filtered = sys.argv[start_of_specify_list:]

    opt_dict['specify_list_of_rcps'] = [int(v) for v in pre_filtered if re.match(r'\d{1,6}', v)]
    opt_dict['id_specified'] = True
    print(f"ri_id's specified: {opt_dict['specify_list_of_rcps']}\n ONLY the 1st will Be processed < DEV")

help_string = f'''\n\n\n
HELP:\n
Mail recipe to blog

EG ./email_recipe_to_blog.py -v -f      # Verbose mode, mail recipe to foodlab live blog

- - - options - - - 
-v          Verbose mode turn on more diagnostics
-f          Go ahead and mail recipe to Foodlab LIVE blog
-a          Mail recipe to Auto-test blog
-e          Mail recipe to email

-d          Leave as draft - DON'T PUBLISH

-i 917      Specify ri_id to process. SB last of arguments

EG:
./email_recipe_to_blog.py -f -i 917    # Mail recipe 917 to live blog
./email_recipe_to_blog.py -e -i 917     # Mail recipe 917 to email

-h          This help
'''

if ('-h' in sys.argv) or ('--h' in sys.argv) or ('-help' in sys.argv) or ('--help' in sys.argv):
    print(help_string)
    sys.exit(0)

from helpers_db import get_user_info_dict_from_DB, get_recipes_for_display_as_list_of_dicts
from helpers_db import set_DB_connection, db_to_use_string

import requests

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

import os
import traceback
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/blogger']



# replace ALL href='https://dtk.health:50015#prawn-cocktail'
# with        href='#prawn-cocktail'
def process_html_for_relative_links(html_content):
    # Pattern to match <a> tags with absolute URLs pointing to the development server
    pattern = r'<a(.*?)href=[\'\"]https://dtk\.health:50015.*?(#.*?)[\'\"](.*?)<\/a>'
    compiled_pattern = re.compile(pattern, re.MULTILINE | re.DOTALL)

    # Function to replace absolute URLs with relative ones
    def replace_with_relative(match):
        before_href, url_path, after_href = match.groups()
        # Construct the new <a> tag with a relative URL
        return f'<a {before_href} href="{url_path}" {after_href}</a>'
    
    # Replace all matches in the HTML content
    processed_html = re.sub(compiled_pattern, replace_with_relative, html_content)
    
    return processed_html


sub_patterns = [
    r'<html>',
    r'<\/html>',
    r'<head>.*?<\/head>',
    r'<script.*?<\/script>',
    r'<script>.*<\/script>',
    r'<!--.*?-->',
]

def process_html_for_posting(html_path, sub_patterns):

    html_body = html_path.read_text()

    for pattern in sub_patterns:
        html_body = re.sub(pattern, '', html_body, flags=re.DOTALL)

    html_body = process_html_for_relative_links(html_body)

    # open blog-post.css and read it into a variable
    
    
    with open(Path('static/recipe_dtk_multi.css'), 'r') as f:
        css = f.read()
    
    html_body = re.sub(r'<body>', f"<body>\n <style>\n{css}\n</style>", html_body, flags=re.DOTALL)

    # mkdir for image file if it doesn't exist
    this_post_img_path = work_dir.joinpath(f"{html_path.stem}_files")
    this_post_img_path.mkdir(exist_ok=True)

    img_lut = {}
    img_lut['img_tags'] = {}
    img_lut['source_file'] = str(html_path)
    # scan html with regex class=\"rcp-image\"\s*?src=['\"](.*?)['\"]> to get all the images
    image_list = re.findall(r'class=\"rcp-image\"\s*?src=[\'\"](.*?)[\'\"]>', html_body)
    url_list = [re.sub('&amp;', '&', image) for image in image_list]
    file_list = [re.sub('%20', ' ', image) for image in url_list]
    count = 0
    pprint(image_list)
    for img, url, file in zip(image_list, url_list, file_list):
        #print(f"img: {img}\nurl: {url}\nfile: {file}")
        image_tag = f"img_tag_{count:03}"
        img_lut['img_tags'][image_tag] = {}
        img_lut['img_tags'][image_tag]['html_img'] = img
        img_lut['img_tags'][image_tag]['db_url'] = url
        img_lut['img_tags'][image_tag]['file'] = file.split('/')[-1]
        img_lut['img_tags'][image_tag]['mail_cid'] = f"cid:{img_lut['img_tags'][image_tag]['file']}"
        count += 1

    print('img_lut - - - - - S')
    pprint(img_lut)
    print('img_lut - - - - - E')

    # request images from server & copy to image directory
    for key, img_set in img_lut['img_tags'].items():
        print(f"img_set['file']: {img_set['file']}")
        request = requests.get(img_set['db_url'], verify=False)        
        with open(this_post_img_path.joinpath(img_set['file']), 'wb') as f:
            f.write(request.content)    

    tagged_html_body = html_body
    for key, img_set in img_lut['img_tags'].items():
        tagged_html_body = tagged_html_body.replace(img_set['html_img'], key)
        html_body = html_body.replace(img_set['html_img'], img_set['mail_cid'])

    # add line in the last row table
    # <tr><td></td></tr><tr><td>If you are in Hereford check out <a href="https://growinglocal.org.uk/">Growing Local</a> for great locally produced veg using organic practices well worth signing up for!</td></tr></table>
    html_body = html_body.rsplit('</table>', 1)   # split at table tag - return list of 2 strings - table tag not in either
    # print('table insert - - - - - S')
    # pprint(tagged_html_body)
    # print('table insert - - - - - M')
    replacement_text = '<tr><td></td></tr><tr><td></td></tr><tr><td colspan="8">If you are in Hereford check out <a href="https://growinglocal.org.uk/this-weeks-veg/">Growing Local</a> for great locally produced veg using organic practices well worth <a href="https://growinglocal.org.uk/join-our-csa/">signing up for!</a></td></tr></table>'
    html_body = replacement_text.join(html_body) # ','.join(['a', 'b']) -> 'a,b'

    img_lut['tagged_html'] = tagged_html_body

    return (img_lut, html_body)


# set image quality to 800px instead of 320px
def update_image_size(content, new_size=800):
    return content.replace('=s320', f'=s{new_size}')


def update_post_image_sizes_title_and_publish(blog_id, target_post_title, service):
    
    target_post = None

    try:
        # cycle through the 1st 5 posts lookin for title matching post_title
        while target_post == None:    
            print(f"Looking for post: {target_post_title}")
            # post might not have been processed yet so possible need to poll until it's present
            draft_posts = service.posts().list(blogId=blog_id, fetchBodies=True, status='DRAFT').execute()
            
            #pprint(draft_posts_request)

            for post in draft_posts.get('items', []):
                print(f"Found: {post['title']}")
                if post['title'] == target_post_title:
                    content = post['content']
                    target_post_id = post['id']
                    updated_content = update_image_size(content)
                    updated_title = post['title'].replace(' - script w css', '')
                    post['title'] = updated_title
                    post['content'] = updated_content
                    
                    # verbose mode
                    print(f"  BLOG ID: [{blog_id}]")
                    print(f"  {post['title']} [{target_post_id}] ({post['url']})")
                    print(f"  {post['content']}")
                    print(f"  {post['title']}")
                    print('.\n.\n.\n')
                    # Update the post
                    updated_post = service.posts().update(blogId=blog_id, postId=target_post_id, body=post).execute()
                    print(f"Post updated: {updated_post['url']}")
                    print('.\n.\n.\n')

                    if opt_dict['leave_as_draft'] == False:
                        # Publish the post
                        target_post = service.posts().publish(blogId=blog_id, postId=target_post_id).execute()
                        #pprint(target_post) 
                        print(f"Post published: {target_post['url']}")
                        print('.\n.\n.\n')
                    else:
                        print(f"Post left as DRAFT: {target_post['url']}")
                        print('.\n.\n.\n')
                    
                    break        
            # wait before polling again
            time.sleep(2)
    
    except Exception as e:
        traceback.print_exc()
        print(f'* * * ERROR * * * : {e}')

    return target_post

target_post_title = 'recipe: red pepper beef bao m - script w css'
#['LIVE', 'DRAFT', 'SCHEDULED']
target_post_state = 'LIVE'

# connect to docker osx
set_DB_connection(db_to_use_string[1])

if __name__ == '__main__':

    if opt_dict['id_specified'] == False:
        # get list of favourite for DB - w/ rcp #'s
        uuid = '014752da-b49d-4fb0-9f50-23bc90e44298'
        user_info = get_user_info_dict_from_DB(uuid)
        recipes = get_recipes_for_display_as_list_of_dicts(user_info['fav_rcp_ids'])
        pprint(recipes)

        # print list of recipes
        print(f'\nRecipes found in FAVS db for usr:{uuid}')
        [print(f"  {r['ri_id']}\t{r['ri_name']}") for i, r in enumerate(recipes)]

        # ask user for recipe ri_id retireve it from DB
        ri_id = int(input("Enter recipe number: "))    

    else:
        ri_id = opt_dict['specify_list_of_rcps'][0]
        recipes = get_recipes_for_display_as_list_of_dicts([ri_id])

    rcp = [r for r in recipes if r['ri_id'] == ri_id]
    #pprint(rcp)
        
    # get recipe from server
    # TODO 1 open chrome with this link - use selenium to do manual step
    #response = requests.get('https://dtk.health:50015/email_debug', params={'ri_id': ri_id}, verify=False)    
    rcp_url = f'https://dtk.health:50015/email_debug?ri_id={ri_id}'
    print(f"\n\nRecipe URL: {rcp_url}")        
    
    import webbrowser
    chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
    webbrowser.get(chrome_path).open(rcp_url)
    # to get th content uses selenium - go manual for now
    # - you have to auto update the driver otherwise it breaks all the time!
    
    # TOUCH FILE    in work_dir - so no titting about with filename when saving
    #               simplify manual save of 411_pork_apple_&_kimchi_bao_m.html
    rcp_name_no_space = rcp[0]['ri_name'].replace(' ', '_')
    post_html_file = work_dir.joinpath(f'{ri_id}_{rcp_name_no_space}.html')
    with open(f'{post_html_file}', 'w') as f:
        f.write('')


    if opt_dict['live_mail']:                
        input(f"\n!! Save the HTML page that opened TO {work_dir}/{post_html_file.name} \n\n. . . Press any key once saved w/ images.")

        img_lut, processed_html = process_html_for_posting(post_html_file, sub_patterns)

        # print('post_html_file - - - - - - -  - - - - - - -  - - - - - - - S')
        # print(processed_html)
        # print('post_html_file - - - - - - -  - - - - - - -  - - - - - - - E')

        img_lut_json_file = work_dir.joinpath(f"{post_html_file.stem}_files").joinpath(f'{ri_id}_{rcp_name_no_space}.json')
        with open(f'{img_lut_json_file}', 'w') as f:
            f.write(json.dumps(img_lut))

        # save processed html to file
        with open(post_html_file, 'w') as f:
            f.write(processed_html)

        subject = f"recipe: {rcp[0]['ri_name']} - script w css"
        body = processed_html
        sender = config['sender']
        recipients = opt_dict['recipients'] #["recipient1@gmail.com", "recipient2@gmail.com"]
        password = config['password']

        assets_path = work_dir.joinpath(f'{post_html_file.stem}_files')
        asset_list = [ ts['file'] for k,ts in img_lut['img_tags'].items() ]

        def send_email(subject, body, sender, recipients, password, assets_path, asset_list=[]):
            msg = MIMEMultipart('related')
            msg['Subject'] = subject #'asset_server'#subject
            msg['From'] = sender
            msg['To'] = ', '.join(recipients)

            # Attach the HTML body
            msg.attach(MIMEText(body, 'html', 'utf-8'))

            for asset in asset_list:
                img_path = assets_path.joinpath(asset)
                
                # Attach the image
                print(f'Attaching: {asset} Exist?:{img_path.exists()}\nP: {img_path}\nAS: <{asset}>')
                with open(img_path, 'rb') as f:
                    img = MIMEImage(f.read())
                
                #underscored_asset = asset.replace(' ', '_')
                img.add_header('Content-ID', f'<{asset}>')  # Use '<myimage>' as the unique identifier
                                                            # refer to it in the html as <img src="cid:myimage">
                msg.attach(img)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
                smtp_server.login(sender, password)
                smtp_server.sendmail(sender, recipients, msg.as_string())
            
            print("Message sent!")

            return msg

        print(f"Sending email to {recipients}: {rcp[0]['ri_name']} - - - - - - - - - - - - - - - - - - - - - - - - - - - - S")
        send_email(subject, body, sender, recipients, password, assets_path, asset_list)
        #pprint(body)
        pprint(asset_list)
        print(f"Sending email to {recipients}: {rcp[0]['ri_name']} - - - - - - - - - - - - - - - - - - - - - - - - - - - - E")

        # Now we have the post & images on blogger we can update the post title & images resolution
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            with open('token.json', 'r') as token:
                creds = credentials.Credentials.from_authorized_user_info(json.load(token), SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'scratch/_email/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('blogger', 'v3', credentials=creds)
        
        update_post_image_sizes_title_and_publish(blog_id, subject, service)


    # See F_20240507_EMAIL_recipe_to_BLOG.rtf for config file info
