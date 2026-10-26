// Intenções iniciais: semeadas no banco só quando a tabela está vazia. Depois disso o banco manda.
export const INTENCOES_PADRAO = [
  {
    nome: 'saudacao',
    frases: ['bom dia', 'boa tarde', 'boa noite', 'tudo bem', 'tudo bom', 'como vai', 'como voce esta', 'e ai', 'eae', 'oi', 'ola', 'opa', 'salve', 'hey', 'hello', 'fala'],
    respostas: [
      { texto: 'Olá! Tudo bem?' },
      { texto: 'Oi! Como você está?' },
      { texto: 'Oi, tudo bem? Em que posso ajudar?' },
      { texto: 'Bom dia! Como você está?', quando: 'bom dia' },
      { texto: 'Boa tarde! Tudo certo?', quando: 'boa tarde' },
      { texto: 'Boa noite! Como você está?', quando: 'boa noite' },
      { texto: 'Tudo bem, e com você?', quando: 'tudo bem' },
      { texto: 'Tudo bem, e com você?', quando: 'tudo bom' },
      { texto: 'Vou bem, obrigado. E você?', quando: 'como vai' },
      { texto: 'Vou bem, obrigado. E você?', quando: 'como voce esta' },
    ],
  },
  {
    nome: 'despedida',
    frases: ['tchau', 'ate logo', 'ate mais', 'ate a proxima', 'ate amanha', 'flw', 'falou', 'adeus', 'xau'],
    respostas: [{ texto: 'Tchau, até a próxima!' }, { texto: 'Até logo! Foi bom falar com você.' }, { texto: 'Até mais!' }],
  },
  {
    nome: 'agradecimento',
    frases: ['obrigado', 'obrigada', 'brigado', 'valeu', 'agradeco'],
    respostas: [{ texto: 'De nada, fico feliz em ajudar.' }, { texto: 'Disponha, estou aqui para isso.' }],
  },
  {
    nome: 'identidade',
    frases: ['qual e o seu nome', 'qual seu nome', 'como voce se chama', 'quem e voce', 'o que voce e'],
    respostas: [{ texto: 'Meu nome é Apolo. Sou uma inteligência artificial que está aprendendo português.' }],
  },
];
