param(
    [string]$file_path
)

Remove-Item ./solidity/output -Recurse -Force -ErrorAction Ignore

docker run --rm `
-v "${PWD}/solidity:/sources" `
ethereum/solc:0.8.20 `
-o /sources/output `
--abi `
--bin `
--evm-version berlin `
/sources/$file_path