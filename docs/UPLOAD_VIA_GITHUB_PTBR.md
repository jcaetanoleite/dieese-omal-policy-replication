# Como publicar pelo site do GitHub, sem Git ou Bash

Este pacote foi refeito depois de um erro do carregamento em uma única operação. Todos os arquivos individuais têm no máximo 8 MiB. Para reduzir também o tamanho de cada confirmação feita pelo navegador, o repositório foi dividido em oito lotes.

## Antes de começar

Depois da mensagem **Commit failed**, volte à página principal do repositório e confira se algum arquivo foi gravado. Se o repositório continuar vazio, inicie pelo lote 1. Se houver arquivos, verifique o commit antes de repetir qualquer lote.

## Como usar os oito lotes

Baixe e extraia cada ZIP. Dentro de cada ZIP há uma pasta chamada `dieese-omal-policy-replication`. Entre nessa pasta e arraste **o conteúdo dela**, não a pasta externa nem o ZIP, para a página **Add file → Upload files**.

Faça os commits nesta ordem:

1. `01_core_code_docs.zip`
2. `02_outputs_processed.zip`
3. `03_raw_data_part_01.zip`
4. `04_raw_data_part_02.zip`
5. `05_raw_data_part_03.zip`
6. `06_raw_data_part_04.zip`
7. `07_raw_data_part_05.zip`
8. `08_raw_data_part_06.zip`

Espere cada commit terminar antes de iniciar o seguinte. Mensagens sugeridas:

- `Add core code and documentation`
- `Add outputs and processed data`
- `Add raw data part 1`
- `Add raw data part 2`
- `Add raw data part 3`
- `Add raw data part 4`
- `Add raw data part 5`
- `Add raw data part 6`

## Arquivos grandes reconstruídos

Três arquivos públicos foram divididos em partes de 8 MiB:

- `Dados_20230713.zip`;
- `tabela7060_19.xlsx`;
- `tabela7060_20.xlsx`.

As partes permanecem no repositório. Para reprodução, o usuário executa:

```text
python src/reassemble_raw_files.py
```

O script concatena as partes e verifica os hashes SHA-256. Não é necessário usar Git LFS para publicar este pacote.
