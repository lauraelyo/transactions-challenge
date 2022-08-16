<!--
title: 'Transactions Challenge'
framework: v3
platform: AWS
language: python
authorLink: 'https://github.com/lauraelyo'
authorName: 'Laura Ramirez'
-->


# Transaction Challenge Function

This Lamdda function takes the uploaded file in csv format from the S3 file system and processes the transactions, each transaction is saved to a dynamoDB table. At the end of the process, an email is sent with the summary of the transactions.

Serverless Framework was used in order to deploy it.

## Prerequisites to deploy
  * Serverless Framework

### Deployment

In order to deploy the lambda, you need to run the following command:

```
$ serverless deploy
```

After running deploy, you should see output similar to:

```bash
Deploying transactions-challenge to stage dev (us-east-1)

✔ Service deployed to stack transactions-challenge-dev (42s)

functions:
  transactions: transactions-challenge-dev-transactions (2.9 kB)
```

### Invocation

After successful deployment, you can upload a file in csv format to the s3 bucket configured.

Sample format for the csv: [transactions.csv](https://github.com/lauraelyo/transactions-challenge/blob/aa5a471de678475954a792bb29eaa9e35379177e/transactions.csv).
