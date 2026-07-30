# Instagram - Prático Soluções

Material completo para montar e manter o Instagram da Prático Soluções.

## Entrega

- foto de perfil com a marca do site;
- sete capas de Destaques;
- 12 posts verticais prontos;
- carrossel com quatro slides;
- oito Stories;
- quatro capas e roteiros de Reels;
- bio, legendas, calendário e textos alternativos;
- instruções do agente Marketing V2;
- gerador reproduzível das artes.

As peças tratam somente dos serviços reais do cliente: serralheria, elétrica, marido de aluguel, manutenção predial, reparos e instalações para residências, condomínios e empresas na região central de São Paulo.

O logotipo aparece nas peças. O WhatsApp `(11) 96526-7558` aparece apenas onde há chamada para orçamento ou confirmação de atendimento.

## Regenerar

```bash
python -m pip install -r marketing/instagram/requirements.txt
python marketing/instagram/scripts/generate_assets.py
python marketing/instagram/scripts/validate_assets.py
```

## Publicação

O agente prepara o material em modo de proposta. Publicação, agendamento, impulsionamento e gastos exigem aprovação humana e conexão real com a Meta.
