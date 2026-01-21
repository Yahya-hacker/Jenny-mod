import shutil
import os

if os.path.exists('Fapcraft_Bedrock_Port.mcaddon'):
    os.remove('Fapcraft_Bedrock_Port.mcaddon')

shutil.make_archive('Fapcraft_Bedrock_Port', 'zip', 'Fapcraft_Bedrock_Port')
os.rename('Fapcraft_Bedrock_Port.zip', 'Fapcraft_Bedrock_Port.mcaddon')
