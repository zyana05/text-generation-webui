@echo off
echo Activating mamba environment 'textgen'...
call mamba activate textgen

echo Starting Text Generation WebUI...
python ../webui/server.py --chat --loader llama.cpp --api --model Qwen2.5-14B-Instruct-Uncensored.i1-Q5_K_S.gguf

pause